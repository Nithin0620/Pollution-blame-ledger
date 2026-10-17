"""Health-burden propagation: population-weighted exposure -> GEMM concentration-response -> attributable deaths.

!! PLACEHOLDERS: the GEMM NCD+LRI parameters below are the all-age pooled values from Burnett et al. (2018, PNAS);
   the real model is age-specific. Baseline mortality, population and adult share are rough Delhi figures.
   Replace with age-stratified GEMM, Delhi SRS/GBD rates and WorldPop before any real claim is made.
"""
from __future__ import annotations
import numpy as np

GEMM = dict(theta=0.1430, theta_se=0.01807, alpha=1.6, mu=15.5, nu=36.8, tmrel=2.4)
BASE_RATE = 0.0028      # adult NCD+LRI deaths / person / year (placeholder)
BASE_RATE_CV = 0.25
ADULT_SHARE = 0.65


def rr(c, theta):
    z = np.clip(c - GEMM["tmrel"], 0, None)
    return np.exp(theta * np.log1p(z / GEMM["alpha"]) / (1 + np.exp(-(z - GEMM["mu"]) / GEMM["nu"])))


def af(c, theta):
    return 1 - 1 / rr(c, theta)


def burden(theta_ks, B, pop_m, sources, days, fractions=(0.5, 1.0), seed=0):
    """theta_ks [D,K,S] episode-mean contribution; B [D,nd] background. Returns per-draw deaths per source & fraction.

    Episode-equivalent deaths = P * adult * y0 * (days/365) * [AF(C) - AF(C - f*c_k)]  (annualisation shortcut).
    """
    rng = np.random.default_rng(seed)
    D, K, S = theta_ks.shape
    bg = B.mean(axis=1)[:, None]                                  # [D,1]
    C = bg + theta_ks.sum(1)                                      # [D,S] modelled station exposure
    th = rng.normal(GEMM["theta"], GEMM["theta_se"], D)[:, None]   # CRF uncertainty
    y0 = BASE_RATE * rng.lognormal(0, BASE_RATE_CV, D)[:, None]    # baseline-rate uncertainty
    pop = (pop_m * 1e6 * ADULT_SHARE)[None, :]
    scale = pop * y0 * days / 365
    out = {"total": (scale * af(C, th)).sum(1)}
    for i, k in enumerate(sources):
        for f in fractions:
            out[f"{k}@{f}"] = (scale * (af(C, th) - af(np.clip(C - f * theta_ks[:, i, :], 0, None), th))).sum(1)
    out["background@1.0"] = (scale * (af(C, th) - af(np.clip(C - bg, 0, None), th))).sum(1)
    return out
