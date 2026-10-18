"""End-to-end: raw station table -> posterior -> ledger (contributions, identifiability, health burden)."""
from __future__ import annotations
import numpy as np
from . import SOURCES, SOURCE_LABELS
from .features import build
from .model import fit
from .diagnostics import identifiability
from .health import burden, admissions, GEMM, BASE_RATE, ADULT_SHARE, ADM_RR_PER10, ADM_BASE_RATE
from .calibration import load as load_calibration, widen


def q(a, ax=0):
    return {"mean": float(np.mean(a)), "lo": float(np.percentile(a, 5)), "hi": float(np.percentile(a, 95))}


def run_inference(df, stations, seed=0, warmup=300, samples=300, chains=2, hourly=True, calibration='default'):
    f = build(df, stations)
    X, y, w = f["X"], f["y"], f["w"]
    post, prior, diag = fit(X, y, seed=seed, warmup=warmup, samples=samples, chains=chains)
    C, B = post["contrib"], post["B"]                          # [D,K,S,T], [D,nd]
    th = C.mean(3)                                             # [D,K,S] episode-mean contribution per station
    names = SOURCES + ["background"]
    pm = np.concatenate([np.einsum("dks,s->dk", th, w), (B.mean(1))[:, None]], axis=1)
    pr = np.concatenate([np.einsum("dks,s->dk", prior["contrib"].mean(3), w), prior["B"].mean(1)[:, None]], axis=1)
    ident = identifiability(pm, pr, names)

    days = y.shape[1] / 24
    bd = burden(th, B, f["pop_m"], SOURCES, days, seed=seed)
    ad = admissions(th, B, f["pop_m"], SOURCES, days, seed=seed + 1)
    total_pm = pm.sum(1)

    comps = []
    for i, n in enumerate(names):
        c = {"id": n, "label": SOURCE_LABELS[n], "mean_ugm3": q(pm[:, i]), "share": q(pm[:, i] / total_pm),
             "status": ident["status"][n]}
        if n != "background":
            c["deaths_50"] = q(bd[f"{n}@0.5"]); c["deaths_100"] = q(bd[f"{n}@1.0"])
            c["adm_50"] = q(ad[f"{n}@0.5"]); c["adm_100"] = q(ad[f"{n}@1.0"])
        else:
            c["deaths_100"] = q(bd["background@1.0"])
        comps.append(c)

    # For flagged trade-off pairs the SUM is the defensible quantity: report it explicitly.
    for p_ in ident["flagged_pairs"]:
        i, j = names.index(p_["a"]), names.index(p_["b"])
        p_["sum_ugm3"] = q(pm[:, i] + pm[:, j])
        if p_["a"] in SOURCES and p_["b"] in SOURCES:
            p_["sum_deaths_100"] = q(bd[f"{p_['a']}@1.0"] + bd[f"{p_['b']}@1.0"])
            p_["sum_adm_100"] = q(ad[f"{p_['a']}@1.0"] + ad[f"{p_['b']}@1.0"])

    result = {"stations": f["stations"], "times": f["times"], "episode_days": days,
              "observed_pm25_popw": (f["y"] * w[:, None]).sum(0).round(1).tolist(),
              "total_pm25": q(total_pm), "total_deaths": q(bd["total"]), "total_adm": q(ad["total"]),
              "components": comps, "identifiability": ident, "sampler": diag,
              "health_assumptions": {"gemm": GEMM, "baseline_rate": BASE_RATE, "adult_share": ADULT_SHARE,
                                     "admissions": {"rr_per10": ADM_RR_PER10, "base_rate": ADM_BASE_RATE},
                                     "note": "Placeholder parameters; mortality is episode-equivalent (annualisation shortcut); admissions use a short-term log-linear CRF."}}
    if hourly:
        # hourly pop-weighted posterior contributions per source
        Bt = np.repeat(B, 24, axis=1)[:, : y.shape[1]]
        H = {}
        for i, n in enumerate(SOURCES):
            h = np.einsum("dst,s->dt", C[:, i], w)
            H[n] = {"mean": h.mean(0).round(2).tolist(), "lo": np.percentile(h, 5, 0).round(2).tolist(),
                    "hi": np.percentile(h, 95, 0).round(2).tolist()}
        H["background"] = {"mean": Bt.mean(0).round(2).tolist(), "lo": np.percentile(Bt, 5, 0).round(2).tolist(),
                           "hi": np.percentile(Bt, 95, 0).round(2).tolist()}
        result["hourly"] = H
        # posterior predictive coverage of observed PM2.5
        mean = Bt[:, None, :] + C.sum(1)
        sobs = post["sigma_obs"][:, None, None]
        rng = np.random.default_rng(seed)
        yrep = mean + rng.normal(size=mean.shape) * sobs
        lo, hi = np.percentile(yrep, [5, 95], axis=0)
        result["ppc_coverage90"] = float(np.mean((y >= lo) & (y <= hi)))
    cal = load_calibration() if calibration == "default" else calibration
    result["calibration"] = widen(result, cal)
    result["_pm"] = pm      # internal (stripped before serialisation)
    result["_w"] = w
    return result
