"""Validation-based interval calibration (split-conformal style).

Raw posterior intervals are over-confident under model misspecification (see validation). We measure, on
held-out synthetic episodes with known truth, how many half-widths the posterior-mean error spans
(k = finite-sample 90th percentile of |error| / half-width, per component) and widen reported intervals by k.
Factors are learned on *calibration* episodes and verified on *separate* evaluation episodes.

CAVEAT: factors learned on synthetic episodes transfer only as far as the synthetic world resembles reality;
re-calibrate on real episodes with independent ground truth (e.g. receptor-model campaigns) when available.
"""
from __future__ import annotations
import json, math, os
import numpy as np

WEAK_K = 2.5   # widening factor at/above which a source can no longer be labelled "identified"
PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibration.json")


def conformal_k(errs, halfw, level=0.9):
    r = np.sort(np.abs(np.asarray(errs)) / np.maximum(np.asarray(halfw), 1e-9))
    n = len(r)
    idx = min(n - 1, math.ceil((n + 1) * level) - 1)
    return float(max(1.0, r[idx]))


def load(path=PATH):
    try:
        return json.load(open(path))
    except Exception:
        return None


def _w(q, k):
    h = k * (q["hi"] - q["lo"]) / 2
    q["raw_lo"], q["raw_hi"] = q["lo"], q["hi"]
    q["lo"], q["hi"] = max(0.0, q["mean"] - h), q["mean"] + h


def widen(result, cal):
    """Widen every reported interval in-place by its component factor. Returns a description for the dashboard."""
    if not cal:
        return {"applied": False}
    k = cal["k"]
    for c in result["components"]:
        kk = k.get(c["id"], 1.0)
        c["calib_k"] = kk
        if kk >= WEAK_K and c["status"] == "identified":      # validation says the raw posterior cannot be trusted here
            c["status"] = "weak"; result["identifiability"]["status"][c["id"]] = "weak"
        for key in ("mean_ugm3", "share", "deaths_50", "deaths_100", "adm_50", "adm_100"):
            if key in c:
                _w(c[key], kk)
    for p in result["identifiability"]["flagged_pairs"]:
        kk = k.get(f"{p['a']}+{p['b']}", k.get(f"{p['b']}+{p['a']}", max(k.get(p["a"], 1.0), k.get(p["b"], 1.0))))
        p["calib_k"] = kk
        for key in ("sum_ugm3", "sum_deaths_100", "sum_adm_100"):
            if key in p:
                _w(p[key], kk)
    for key in ("total_pm25", "total_deaths", "total_adm"):
        _w(result[key], k.get("total", 1.0) if "total" in k else 1.0)
    return {"applied": True, "k": k, "n_episodes": cal.get("n_episodes"), "level": cal.get("level", 0.9),
            "learned_on": cal.get("learned_on", "synthetic"), "note": "Intervals widened by validation-derived factors; see ledger/calibration.py."}
