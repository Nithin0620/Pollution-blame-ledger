"""Hierarchical Bayesian receptor model, sampled with NUTS (NumPyro).

PM2.5[s,t] = B[day(t)] + sum_k theta[k,s] * g[k,s,day(t)] * (X[k,s,t] - a_k) / (1 - a_k) + eps
  * theta >= 0 (log-normal), partially pooled across stations: theta[k,s] = exp(mu_k + sigma_k * z_ks)
  * a[k,s] = non-source baseline of tracer k. Physical bound: sources only add, so a <= min_t X. a = u_k * min_t X[k,s],
    u_k ~ Beta(.) - the prior's concentration is the structural assumption varied across the ensemble. Fixed at 0 for fire radiative power, which has a true zero.
  * L[k,j] = cross-talk: share of tracer k that really comes from source j (e.g. fires also emit CO/NO2/SO2).
    Proxy shapes are un-mixed to first order:  s_k = (P_k - sum_j L_kj P_j) / (1 - sum_j L_kj)   (mean-one preserved)
  * g = mean-one log-normal station-day gain: honest allowance for proxy/source mismatch (timing, transport lag, tracer cross-talk)
  * B = regional background, non-negative log random walk at daily resolution
  * X[k] = unit-mean tracer proxies (see features.py), already ventilation-modulated
"""
from __future__ import annotations
import numpy as np
import jax, jax.numpy as jnp
import numpyro, numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS, Predictive

numpyro.set_host_device_count(2)


def receptor_model(X, y=None, u_ab=(3.0, 2.0)):
    K, S, T = X.shape
    nd = T // 24
    mu = numpyro.sample("mu", dist.Normal(jnp.log(15.0), 0.9).expand([K]))
    sig = numpyro.sample("sigma", dist.HalfNormal(0.5).expand([K]))
    z = numpyro.sample("z", dist.Normal(0, 1).expand([K, S]))
    theta = numpyro.deterministic("theta", jnp.exp(mu[:, None] + sig[:, None] * z))
    lb0 = numpyro.sample("lb0", dist.Normal(jnp.log(40.0), 0.6))
    tau = numpyro.sample("tau", dist.HalfNormal(0.25))
    steps = numpyro.sample("steps", dist.Normal(0, 1).expand([nd - 1]))
    logB = lb0 + tau * jnp.concatenate([jnp.zeros(1), jnp.cumsum(steps)])
    B = numpyro.deterministic("B", jnp.exp(logB))
    Bt = jnp.repeat(B, 24)[:T]
    u_free = numpyro.sample("a_free", dist.Beta(*u_ab).expand([K - 1]))
    u = jnp.concatenate([u_free, jnp.zeros(1)])                                   # last source = biomass (FRP)
    a = numpyro.deterministic("a", u[:, None] * jnp.min(X, axis=2))               # [K,S]
    tau_g = numpyro.sample("tau_g", dist.HalfNormal(0.3).expand([K]))
    eps = numpyro.sample("eps", dist.Normal(0, 1).expand([K, S, nd]))
    g = jnp.exp(tau_g[:, None, None] * eps - 0.5 * tau_g[:, None, None] ** 2)
    P = jnp.maximum(X - a[:, :, None], 0.0) / (1 - a[:, :, None])                 # unit-mean tracer shapes
    L = numpyro.sample("L", dist.HalfNormal(0.2).expand([K, K]))
    L = L * (1 - jnp.eye(K))
    L = L * jnp.minimum(1.0, 0.6 / jnp.maximum(L.sum(1, keepdims=True), 1e-6))     # cap total cross-talk at 60 %
    numpyro.deterministic("L_used", L)
    shape = jnp.maximum(P - jnp.einsum("kj,jst->kst", L, P), 0.0) / (1 - L.sum(1))[:, None, None]
    contrib = theta[:, :, None] * jnp.repeat(g, 24, axis=2)[:, :, :T] * shape
    numpyro.deterministic("contrib", contrib)
    mean = Bt[None, :] + contrib.sum(0)
    s_obs = numpyro.sample("sigma_obs", dist.HalfNormal(15.0))
    numpyro.sample("y", dist.Normal(mean, s_obs), obs=y)


# Structural-uncertainty ensemble: how close is the tracer's non-source baseline to its observed minimum?
#   (1,1) = no idea;  (3,2) = moderately close;  (6,1.5) = very close.   Draws from all variants are pooled with equal weight.
VARIANTS = [(3.0, 2.0)]   # add (1,1),(6,1.5) for a wider structural ensemble (2-3x slower)
_CHECK = ("theta", "mu", "sigma", "sigma_obs", "B", "a_free", "tau_g", "L_used")


def _fit_once(X, y, u_ab, seed, warmup, samples, chains):
    model = lambda X, y=None: receptor_model(X, y, u_ab)
    mcmc = MCMC(NUTS(model, target_accept_prob=0.9), num_warmup=warmup, num_samples=samples,
                num_chains=chains, chain_method="parallel", progress_bar=False)
    mcmc.run(jax.random.PRNGKey(seed), jnp.asarray(X), jnp.asarray(y), extra_fields=("diverging",))
    post = {k: np.asarray(v) for k, v in mcmc.get_samples().items() if k in ("contrib", "B", "sigma_obs")}
    summ = numpyro.diagnostics.summary({k: v for k, v in mcmc.get_samples(group_by_chain=True).items() if k in _CHECK},
                                       prob=0.9, group_by_chain=True)
    rhat = float(np.nanmax([np.nanmax(v["r_hat"]) for v in summ.values()]))
    ess = float(np.nanmin([np.nanmin(v["n_eff"]) for v in summ.values()]))
    div = int(np.sum(mcmc.get_extra_fields()["diverging"]))
    prior = Predictive(model, num_samples=500)(jax.random.PRNGKey(seed + 99), jnp.asarray(X))
    prior = {k: np.asarray(v) for k, v in prior.items() if k in ("contrib", "B")}
    return post, prior, rhat, ess, div


def _fit_one(X, y, u_ab, seed, warmup, samples, chains, max_rhat=1.1, retries=3):
    """NUTS can park a chain in a bad mode on hard (real, multi-station) data: re-seed until chains agree."""
    best = None
    for r in range(retries):
        out = _fit_once(X, y, u_ab, seed + 7919 * r, warmup, samples, chains)
        out[2:]  # (post, prior, rhat, ess, div)
        if best is None or out[2] < best[2]:
            best = out
        if out[2] <= max_rhat:
            break
    return best


def fit(X, y, seed=0, warmup=300, samples=300, chains=2, variants=VARIANTS):
    posts, priors, rh, es, dv = [], [], [], [], []
    for j, u_ab in enumerate(variants):
        p, pr, r, e, d = _fit_one(X, y, u_ab, seed + 1000 * j, warmup, samples, chains)
        posts.append(p); priors.append(pr); rh.append(r); es.append(e); dv.append(d)
    cat = lambda L: {k: np.concatenate([x[k] for x in L]) for k in L[0]}
    return cat(posts), cat(priors), {"max_rhat": max(rh), "min_ess": min(es), "divergences": int(sum(dv)),
                                      "variants": len(variants)}
