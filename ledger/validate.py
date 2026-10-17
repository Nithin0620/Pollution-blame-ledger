"""Falsification: recover KNOWN synthetic ground truth, check credible-interval calibration, plume-injection test."""
from __future__ import annotations
import numpy as np
from . import SOURCES
from .synth import simulate
from .pipeline import run_inference


def truth_means(truth, w):
    c = truth["contrib"]                         # [K,S,T]
    return np.append((c.mean(2) * w[None, :]).sum(1), truth["background"].mean())


def run_validation(n_episodes=10, base_seed=100, warmup=300, samples=300, log=print):
    names = SOURCES + ["background"]
    rows, cover = [], {n: [] for n in names}
    ppc = []
    for e in range(n_episodes):
        df, st, truth = simulate(seed=base_seed + e)
        r = run_inference(df, st, seed=e, warmup=warmup, samples=samples)
        tm = truth_means(truth, r["_w"])
        for i, n in enumerate(names):
            c = r["components"][i]
            lo, hi, mean = c["mean_ugm3"]["lo"], c["mean_ugm3"]["hi"], c["mean_ugm3"]["mean"]
            cover[n].append(bool(lo <= tm[i] <= hi))
            rows.append({"episode": e, "source": n, "truth": float(tm[i]), "est": mean, "lo": lo, "hi": hi})
        ppc.append(r["ppc_coverage90"])
        log(f"  validation episode {e + 1}/{n_episodes} done (rhat {r['sampler']['max_rhat']:.3f})")
    # Pair-sum calibration for the trade-off pair that matters most (traffic + biomass share the night-time ventilation signal)
    pair = {}
    for a, b in [("traffic", "biomass")]:
        ok = []
        for e in range(n_episodes):
            ra = next(x for x in rows if x["episode"] == e and x["source"] == a)
            rb = next(x for x in rows if x["episode"] == e and x["source"] == b)
            ok.append(abs((ra["est"] + rb["est"]) - (ra["truth"] + rb["truth"])) / (ra["truth"] + rb["truth"]))
        pair[f"{a}+{b}"] = {"median_rel_err": float(np.median(ok))}
    per = {}
    for n in names:
        sub = [x for x in rows if x["source"] == n]
        err = np.array([x["est"] - x["truth"] for x in sub])
        per[n] = {"coverage90": float(np.mean(cover[n])), "rmse": float(np.sqrt((err ** 2).mean())),
                  "bias": float(err.mean()), "mean_truth": float(np.mean([x["truth"] for x in sub]))}

    # plume injection: double one source with everything else (incl. noise seed) identical
    inj = []
    for k in ["biomass", "traffic"]:
        df0, st, tr0 = simulate(seed=base_seed + 500)
        df1, _, tr1 = simulate(seed=base_seed + 500, scale={k: 2.0})
        r0 = run_inference(df0, st, seed=1, warmup=warmup, samples=samples, hourly=False)
        r1 = run_inference(df1, st, seed=1, warmup=warmup, samples=samples, hourly=False)
        i = SOURCES.index(k)
        d_post = r1["_pm"][:, i] - r0["_pm"][:, i]   # not paired draws, but independent => conservative difference of means
        t0, t1 = truth_means(tr0, r0["_w"])[i], truth_means(tr1, r1["_w"])[i]
        a, b = r0["components"][i]["mean_ugm3"], r1["components"][i]["mean_ugm3"]
        inj.append({"source": k, "true_before": float(t0), "true_after": float(t1),
                    "est_before": a["mean"], "est_after": b["mean"],
                    "ci_after": [b["lo"], b["hi"]], "truth_in_ci": bool(b["lo"] <= t1 <= b["hi"]),
                    "detected_increase": bool(b["lo"] > a["hi"] or b["mean"] > a["mean"] * 1.4)})
        log(f"  injection test: {k}")
    return {"n_episodes": n_episodes, "per_source": per, "points": rows,
            "pair_sum_error": pair, "ppc_coverage90_mean": float(np.mean(ppc)), "injection": inj,
            "note": "Each synthetic episode is unseen by construction: priors are fixed, nothing is retrained between episodes."}
