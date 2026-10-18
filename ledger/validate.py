"""Falsification + calibration on synthetic episodes with KNOWN ground truth.

  1. Calibration set: learn per-component interval-widening factors (ledger/calibration.py).
  2. Evaluation set (different seeds): report coverage/RMSE/bias BEFORE and AFTER calibration.
  3. Plume injection: double one source, check the ledger notices.
Each synthetic episode is unseen by construction: priors are fixed and nothing is retrained between episodes.
"""
from __future__ import annotations
import json, os
import numpy as np
from . import SOURCES
from .synth import simulate
from .pipeline import run_inference
from .calibration import conformal_k, PATH

NAMES = SOURCES + ["background"]
PAIRS = [("traffic", "biomass"), ("dust", "background")]


def truth_means(truth, w):
    c = truth["contrib"]
    return np.append((c.mean(2) * w[None, :]).sum(1), truth["background"].mean())


def _episode(seed, e, warmup, samples):
    df, st, truth = simulate(seed=seed)
    r = run_inference(df, st, seed=e, warmup=warmup, samples=samples, hourly=True, calibration=None)
    tm = truth_means(truth, r["_w"]); pm = r["_pm"]
    rec = {}
    for i, n in enumerate(NAMES):
        lo, hi = np.percentile(pm[:, i], [5, 95])
        rec[n] = dict(truth=float(tm[i]), est=float(pm[:, i].mean()), lo=float(lo), hi=float(hi))
    for a, b in PAIRS:
        i, j = NAMES.index(a), NAMES.index(b); s = pm[:, i] + pm[:, j]
        lo, hi = np.percentile(s, [5, 95])
        rec[f"{a}+{b}"] = dict(truth=float(tm[i] + tm[j]), est=float(s.mean()), lo=float(lo), hi=float(hi))
    return rec, r["ppc_coverage90"], r["sampler"]["max_rhat"]


def run_validation(n_cal=12, n_eval=8, base_seed=100, warmup=300, samples=300, log=print, save_calibration=True):
    keys = NAMES + [f"{a}+{b}" for a, b in PAIRS]
    cal, ev, ppc = [], [], []
    for e in range(n_cal + n_eval):
        seed = base_seed + (e if e < n_cal else 100 + e)
        rec, pc, rh = _episode(seed, e, warmup, samples)
        (cal if e < n_cal else ev).append(rec)
        if e >= n_cal: ppc.append(pc)
        log(f"  validation episode {e + 1}/{n_cal + n_eval} ({'calibration' if e < n_cal else 'held-out'}) rhat={rh:.3f}")

    k = {}
    for key in keys:
        err = [r[key]["est"] - r[key]["truth"] for r in cal]
        hw = [(r[key]["hi"] - r[key]["lo"]) / 2 for r in cal]
        k[key] = conformal_k(err, hw)
    calib = {"k": k, "n_episodes": n_cal, "level": 0.9, "learned_on": "synthetic"}
    if save_calibration:
        json.dump(calib, open(PATH, "w"), indent=1)

    per, pts = {}, []
    for key in keys:
        err = np.array([r[key]["est"] - r[key]["truth"] for r in ev])
        raw = [r[key]["lo"] <= r[key]["truth"] <= r[key]["hi"] for r in ev]
        cl = []
        for r in ev:
            h = k[key] * (r[key]["hi"] - r[key]["lo"]) / 2
            lo, hi = max(0, r[key]["est"] - h), r[key]["est"] + h
            cl.append(lo <= r[key]["truth"] <= hi)
            if key in NAMES:
                pts.append({"source": key, "truth": r[key]["truth"], "est": r[key]["est"], "lo": lo, "hi": hi})
        per[key] = {"coverage90_raw": float(np.mean(raw)), "coverage90_cal": float(np.mean(cl)), "k": k[key],
                    "rmse": float(np.sqrt((err ** 2).mean())), "bias": float(err.mean()),
                    "mean_truth": float(np.mean([r[key]["truth"] for r in ev])),
                    "rel_err_median": float(np.median(np.abs(err) / np.array([r[key]["truth"] for r in ev])))}

    # plume injection (uses calibrated intervals)
    inj = []
    for kk in ["biomass", "traffic"]:
        sd = base_seed + 500
        df0, st, tr0 = simulate(seed=sd); df1, _, tr1 = simulate(seed=sd, scale={kk: 2.0})
        r0 = run_inference(df0, st, seed=1, warmup=warmup, samples=samples, hourly=False, calibration=calib)
        r1 = run_inference(df1, st, seed=1, warmup=warmup, samples=samples, hourly=False, calibration=calib)
        i = SOURCES.index(kk)
        t0, t1 = truth_means(tr0, r0["_w"])[i], truth_means(tr1, r1["_w"])[i]
        a, b = r0["components"][i]["mean_ugm3"], r1["components"][i]["mean_ugm3"]
        inj.append({"source": kk, "true_before": float(t0), "true_after": float(t1),
                    "est_before": a["mean"], "est_after": b["mean"], "ci_after": [b["lo"], b["hi"]],
                    "truth_in_ci": bool(b["lo"] <= t1 <= b["hi"]), "detected_increase": bool(b["mean"] > a["mean"] * 1.25)})
        log(f"  injection test: {kk}")
    return {"n_cal": n_cal, "n_eval": n_eval, "per_source": per, "points": pts, "calibration": calib,
            "ppc_coverage90_mean": float(np.mean(ppc)), "injection": inj,
            "note": "Calibration factors were learned on separate episodes from the ones scored here (held-out)."}
