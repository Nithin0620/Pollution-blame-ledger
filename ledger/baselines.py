"""Baseline receptor methods scored on the SAME held-out synthetic episodes as the Bayesian model.

Why: a reviewer's first question is "does the Bayesian machinery beat something simple?"  Two baselines:
  * nnls         - classical non-negative least squares on the same tracer proxies (population-weighted):
                   PM2.5(t) = b + sum_k c_k X_k(t),  c >= 0.  Intervals from a day-block bootstrap.
                   This is the regression core of CMB-style receptor modelling.
  * fixed_shares - a static published split (IIT Kanpur winter CMB, via CSE India) applied to the episode's
                   observed PM2.5.  This is what "just quote the report" does on a new event.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import nnls
from . import SOURCES
from .synth import simulate
from .features import build
from .validate import NAMES, PAIRS, truth_means

# IIT Kanpur winter split mapped onto our categories (coal/fly ash -> industry; secondary + solid-waste burning -> unresolved)
FIXED_SHARES = {"traffic": 0.25, "industry": 0.05, "dust": 0.06, "biomass": 0.26, "background": 0.38}


def _nnls_fit(Xw, yw):
    A = np.column_stack([np.ones_like(yw), Xw.T])
    coef, _ = nnls(A, yw)
    return coef[0], coef[1:]


def nnls_episode(df, st, boots=200, seed=0):
    f = build(df, st)
    w = f["w"]
    Xw = np.einsum("kst,s->kt", f["X"], w)
    yw = (f["y"] * w[:, None]).sum(0)
    b, c = _nnls_fit(Xw, yw)
    est = np.append(c * Xw.mean(1), b)
    nd = len(yw) // 24
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(boots):
        days = rng.integers(0, nd, nd)
        idx = np.concatenate([np.arange(d * 24, d * 24 + 24) for d in days])
        bb, cc = _nnls_fit(Xw[:, idx], yw[idx])
        draws.append(np.append(cc * Xw[:, idx].mean(1), bb))
    return est, np.array(draws), yw.mean()


def _score(rows):
    out = {}
    for key, r in rows.items():
        t, e = np.array(r["truth"]), np.array(r["est"])
        err = e - t
        d = {"rmse": float(np.sqrt((err ** 2).mean())), "bias": float(err.mean()),
             "rel_err_median": float(np.median(np.abs(err) / t))}
        if r.get("lo"):
            d["coverage90_raw"] = float(np.mean((np.array(r["lo"]) <= t) & (t <= np.array(r["hi"]))))
            d["width"] = float(np.mean(np.array(r["hi"]) - np.array(r["lo"])))
        out[key] = d
    return out


def run_baselines(val, base_seed=100, log=print):
    """Score baselines on the same held-out episodes used in `val` (seed = base_seed + 100 + e for e >= n_cal)."""
    n_cal, n_eval = val["n_cal"], val["n_eval"]
    keys = NAMES + [f"{a}+{b}" for a, b in PAIRS]
    rows = {m: {k: {"truth": [], "est": [], "lo": [], "hi": []} for k in keys} for m in ("nnls", "fixed_shares")}
    for e in range(n_cal, n_cal + n_eval):
        df, st, truth = simulate(seed=base_seed + 100 + e)
        w = build(df, st)["w"]
        tm = truth_means(truth, w)
        est, dr, ymean = nnls_episode(df, st, seed=e)
        fx = np.array([FIXED_SHARES[n] for n in NAMES]) * ymean
        for m, point, lo, hi in (("nnls", est, np.percentile(dr, 5, 0), np.percentile(dr, 95, 0)), ("fixed_shares", fx, None, None)):
            for i, n in enumerate(NAMES):
                R = rows[m][n]; R["truth"].append(tm[i]); R["est"].append(point[i])
                if lo is not None: R["lo"].append(lo[i]); R["hi"].append(hi[i])
            for a, b in PAIRS:
                i, j = NAMES.index(a), NAMES.index(b); R = rows[m][f"{a}+{b}"]
                R["truth"].append(tm[i] + tm[j]); R["est"].append(point[i] + point[j])
                if lo is not None:
                    s = dr[:, i] + dr[:, j]; R["lo"].append(np.percentile(s, 5)); R["hi"].append(np.percentile(s, 95))
        log(f"  baseline episode {e - n_cal + 1}/{n_eval}")
    scored = {m: _score(rows[m]) for m in rows}
    bayes = {k: {"rmse": v["rmse"], "bias": v["bias"], "rel_err_median": v["rel_err_median"],
                 "coverage90_raw": v["coverage90_raw"], "coverage90_cal": v["coverage90_cal"]}
             for k, v in val["per_source"].items()}
    scored["bayes"] = bayes
    return scored


def run_shift_test(calib, n=8, base_seed=700, warmup=300, samples=300, log=print, gen=None, shift=True):
    """'New event' stress test: each episode has its source mix deliberately SHIFTED (each source scaled by a random
    factor in [0.4, 2.5]) so it no longer resembles any published split.  Scores Bayes (calibrated intervals),
    NNLS and the fixed published split against known truth."""
    from .pipeline import run_inference
    rng = np.random.default_rng(base_seed)
    keys = NAMES + [f"{a}+{b}" for a, b in PAIRS]
    rows = {m: {k: {"truth": [], "est": [], "lo": [], "hi": []} for k in keys} for m in ("bayes", "nnls", "fixed_shares")}
    episodes = []
    for e in range(n):
        sc = {s: float(np.exp(rng.uniform(np.log(0.4), np.log(2.5)))) for s in SOURCES} if shift else {}
        df, st, truth = (gen or simulate)(seed=base_seed + e, scale=sc)
        r = run_inference(df, st, seed=e, warmup=warmup, samples=samples, hourly=False, calibration=calib)
        tm = truth_means(truth, r["_w"])
        est, dr, ymean = nnls_episode(df, st, seed=e)
        fx = np.array([FIXED_SHARES[k] for k in NAMES]) * ymean
        bm = {c["id"]: c["mean_ugm3"] for c in r["components"]}
        pm = r["_pm"]
        for i, nme in enumerate(NAMES):
            lo, hi, mean = bm[nme]["lo"], bm[nme]["hi"], bm[nme]["mean"]
            rows["bayes"][nme]["lo"].append(lo); rows["bayes"][nme]["hi"].append(hi)
            for m, pt in (("bayes", mean), ("nnls", est[i]), ("fixed_shares", fx[i])):
                rows[m][nme]["truth"].append(tm[i]); rows[m][nme]["est"].append(pt)
            rows["nnls"][nme]["lo"].append(np.percentile(dr[:, i], 5)); rows["nnls"][nme]["hi"].append(np.percentile(dr[:, i], 95))
        for a, b in PAIRS:
            i, j = NAMES.index(a), NAMES.index(b); key = f"{a}+{b}"
            s = pm[:, i] + pm[:, j]; kk = (calib or {}).get("k", {}).get(key, 1.0)
            h = kk * (np.percentile(s, 95) - np.percentile(s, 5)) / 2
            rows["bayes"][key]["lo"].append(max(0, s.mean() - h)); rows["bayes"][key]["hi"].append(s.mean() + h)
            sn = dr[:, i] + dr[:, j]
            rows["nnls"][key]["lo"].append(np.percentile(sn, 5)); rows["nnls"][key]["hi"].append(np.percentile(sn, 95))
            for m, pt in (("bayes", s.mean()), ("nnls", est[i] + est[j]), ("fixed_shares", fx[i] + fx[j])):
                rows[m][key]["truth"].append(tm[i] + tm[j]); rows[m][key]["est"].append(pt)
        episodes.append({"scale": sc, "truth_shares": {n_: float(tm[i] / tm.sum()) for i, n_ in enumerate(NAMES)}})
        log(f"  shifted episode {e + 1}/{n}")
    for m in ("fixed_shares",):
        for k in keys: rows[m][k]["lo"] = []; rows[m][k]["hi"] = []
    out = {m: _score(rows[m]) for m in rows}
    out["episodes"] = episodes
    out["n"] = n
    return out
