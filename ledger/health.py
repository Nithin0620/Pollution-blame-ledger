"""Health-burden propagation: population-weighted exposure -> GEMM concentration-response -> attributable deaths.

VERIFIED: GEMM NCD+LRI parameters (ages 25+, all regions incl. China) were checked against the authors' data release
   ("GEMM Calculator (PNAS).xlsx", sheet "GEMM fit parameters"; github.com/mszyszkowicz/DataGEMM):
   theta=0.1430 (SE 0.01807), alpha=1.6, mu=15.5, nu=36.8; counterfactual 2.4 ug/m3. Burnett et al. 2018, PNAS 115(38).
   GEMM_EX_CHINA holds the authors' alternative fit excluding China, used as a sensitivity check.
PLACEHOLDER: baseline mortality rate, adult share, and the admissions function are NOT yet sourced from Delhi data.
"""
from __future__ import annotations
import numpy as np

GEMM = dict(theta=0.1430, theta_se=0.01807, alpha=1.6, mu=15.5, nu=36.8, tmrel=2.4)
GEMM_EX_CHINA = dict(theta=0.1231, theta_se=0.01797, alpha=1.5, mu=10.4, nu=25.9, tmrel=2.4)  # sensitivity variant
BASE_RATE = 0.0028      # adult NCD+LRI deaths / person / year (placeholder)
BASE_RATE_CV = 0.25
ADULT_SHARE = 0.65


def rr(c, theta, g=None):
    g = g or GEMM
    z = np.clip(c - g["tmrel"], 0, None)
    return np.exp(theta * np.log1p(z / g["alpha"]) / (1 + np.exp(-(z - g["mu"]) / g["nu"])))


def af(c, theta, g=None):
    return 1 - 1 / rr(c, theta, g)


def burden(theta_ks, B, pop_m, sources, days, fractions=(0.5, 1.0), seed=0, gemm=None):
    """theta_ks [D,K,S] episode-mean contribution; B [D,nd] background. Returns per-draw deaths per source & fraction.

    Episode-equivalent deaths = P * adult * y0 * (days/365) * [AF(C) - AF(C - f*c_k)]  (annualisation shortcut).
    """
    g = gemm or GEMM
    rng = np.random.default_rng(seed)
    D, K, S = theta_ks.shape
    bg = B.mean(axis=1)[:, None]                                  # [D,1]
    C = bg + theta_ks.sum(1)                                      # [D,S] modelled station exposure
    th = rng.normal(g["theta"], g["theta_se"], D)[:, None]   # CRF uncertainty
    y0 = BASE_RATE * rng.lognormal(0, BASE_RATE_CV, D)[:, None]    # baseline-rate uncertainty
    pop = (pop_m * 1e6 * ADULT_SHARE)[None, :]
    scale = pop * y0 * days / 365
    out = {"total": (scale * af(C, th, g)).sum(1)}
    for i, k in enumerate(sources):
        for f in fractions:
            out[f"{k}@{f}"] = (scale * (af(C, th, g) - af(np.clip(C - f * theta_ks[:, i, :], 0, None), th, g))).sum(1)
    out["background@1.0"] = (scale * (af(C, th, g) - af(np.clip(C - bg, 0, None), th, g))).sum(1)
    return out


# ---- Morbidity: short-term cardio-respiratory hospital admissions (PLACEHOLDER parameters) ----
# Log-linear CRF. NOTE: 1.008 per 10 ug/m3 is a placeholder. Published short-term MORTALITY estimates (Lancet Planet Health 2024,
# 10 Indian cities) are +1.4% pooled / +0.31% Delhi per 10 ug/m3; admissions-specific Indian estimates still to be sourced.
ADM_RR_PER10 = 1.008
ADM_RR_SE_LOG = 0.0025          # SE of ln(RR per 10)
ADM_BASE_RATE = 0.004           # cardio-respiratory admissions / person / year (placeholder)
ADM_BASE_CV = 0.30


def admissions(theta_ks, B, pop_m, sources, days, fractions=(0.5, 1.0), seed=1):
    """Episode-attributable hospital admissions per source (same counterfactuals as `burden`)."""
    rng = np.random.default_rng(seed)
    D, K, S = theta_ks.shape
    bg = B.mean(axis=1)[:, None]
    C = bg + theta_ks.sum(1)
    beta = rng.normal(np.log(ADM_RR_PER10), ADM_RR_SE_LOG, D)[:, None] / 10.0
    y0 = ADM_BASE_RATE * rng.lognormal(0, ADM_BASE_CV, D)[:, None]
    scale = (pop_m * 1e6)[None, :] * y0 * days / 365
    afa = lambda c: 1 - np.exp(-beta * c)
    out = {"total": (scale * afa(C)).sum(1)}
    for i, k in enumerate(sources):
        for f in fractions:
            out[f"{k}@{f}"] = (scale * (afa(C) - afa(np.clip(C - f * theta_ks[:, i, :], 0, None)))).sum(1)
    out["background@1.0"] = (scale * (afa(C) - afa(np.clip(C - bg, 0, None)))).sum(1)
    return out
