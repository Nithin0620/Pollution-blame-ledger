"""Out-of-model checks on REAL data (six Delhi CPCB/DPCC stations + NASA FIRMS fire power, autumn 2018).

No source-level ground truth exists for real air, so we test what can be tested independently:
  1. Posterior-predictive coverage of observed PM2.5 (does the model reproduce reality?)
  2. Directional check: crop-burning contribution should be higher in the burning peak than before/after it,
     judged by the posterior probability, with fire detections (independent satellite data) as the reference
  3. Literature overlap of the shares (IIT Kanpur / CEEW ranges)
  4. Convergence diagnostics
"""
from __future__ import annotations
import numpy as np
from . import SOURCES
from .realdata import load_fire_daily, to_episode_multi
from .pipeline import run_inference

WINDOWS = {"before": ("2018-09-20", "2018-10-04"), "peak": ("2018-10-28", "2018-11-11"), "after": ("2018-11-26", "2018-12-10")}
NAMES = SOURCES + ["background"]


def run_real_checks(fire_csv, log=print, seed=3, warmup=400, samples=400):
    fd = load_fire_daily(fire_csv)
    eps, summ, draws = {}, {}, {}
    for k, (a, b) in WINDOWS.items():
        df, st = to_episode_multi(fd, a, b)
        r = run_inference(df, st, seed=seed, warmup=warmup, samples=samples, hourly=True)
        draws[k] = r["_pm"]
        fire = float(fd.reindex(__import__("pandas").date_range(a, b, inclusive="left")).fillna(0).mean())
        summ[k] = {"window": [a, b], "mean_pm25_obs": float((df.pm25.to_numpy().reshape(len(st), -1) * (st.pop_m.to_numpy() / st.pop_m.sum())[:, None]).sum(0).mean()), "mean_fire_frp_mw": fire,
                   "ppc_coverage90": r["ppc_coverage90"], "max_rhat": r["sampler"]["max_rhat"],
                   "min_ess": r["sampler"]["min_ess"], "divergences": r["sampler"]["divergences"],
                   "shares": {x["id"]: x["share"] for x in r["components"]},
                   "mean_ugm3": {x["id"]: x["mean_ugm3"] for x in r["components"]},
                   "literature": r["literature"], "flagged_pairs": [[p["a"], p["b"]] for p in r["identifiability"]["flagged_pairs"]]}
        eps[k] = r
        log(f"  real window {k}: PM2.5 {summ[k]['mean_pm25_obs']:.0f}, PPC {r['ppc_coverage90']:.2f}")
    i = NAMES.index("biomass"); rng = np.random.default_rng(0)
    def p_gt(a, b):
        x, y = draws[a][:, i], draws[b][:, i]
        n = min(len(x), len(y)); return float(np.mean(rng.permutation(x)[:n] > rng.permutation(y)[:n]))
    out = {"windows": summ,
           "biomass_direction": {"p_peak_gt_before": p_gt("peak", "before"), "p_peak_gt_after": p_gt("peak", "after"),
                                 "fire_ratio_peak_to_after": summ["peak"]["mean_fire_frp_mw"] / max(summ["after"]["mean_fire_frp_mw"], 1e-9),
                                 "note": "Posterior probability that the burning contribution (ug/m3) is higher in the peak window than before/after."},
           "station": f"{len(st)} Delhi stations (CPCB/DPCC)",
           "caveats": ["Six stations share one airshed meteorology (cross-station median); boundary-layer height is a solar-radiation proxy; fire-footprint is regional daily FRP with a fixed 5-18 h lag.",
                       "The CPCB files appear gap-filled by interpolation.", "Station population weights are a placeholder (equal split of ~20 M).", "No source-level ground truth: these are consistency checks, not accuracy measurements."]}
    return out, eps
