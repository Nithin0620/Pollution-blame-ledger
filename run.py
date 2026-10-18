#!/usr/bin/env python
"""Pollution Blame Ledger - MVP runner.

  python run.py --demo                      # synthetic Delhi episode (known truth) + validation + dashboard
  python run.py --csv obs.csv --stations stations.csv   # real data in the documented schema
"""
import argparse, json, os, sys, time
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger.synth import simulate
from ledger.pipeline import run_inference
from ledger.validate import run_validation, truth_means


def clean(r):
    return {k: v for k, v in r.items() if not k.startswith("_")}


def build_dashboard(out, results, validation):
    tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard", "template.html"), encoding="utf-8").read()
    payload = json.dumps({"results": results, "validation": validation})
    open(os.path.join(out, "dashboard.html"), "w", encoding="utf-8").write(tpl.replace("/*__DATA__*/null", payload))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--csv"); ap.add_argument("--stations")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--cal-episodes", type=int, default=12)
    ap.add_argument("--eval-episodes", type=int, default=8)
    ap.add_argument("--skip-validation", action="store_true")
    ap.add_argument("--out", default="outputs")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    if a.demo:
        df, st, truth = simulate(seed=a.seed)
        df.to_csv(os.path.join(a.out, "demo_observations.csv"), index=False)
        st.to_csv(os.path.join(a.out, "demo_stations.csv"), index=False)
        source = "synthetic"
    elif a.csv and a.stations:
        df = pd.read_csv(a.csv, parse_dates=["datetime"]); st = pd.read_csv(a.stations); truth = None
        source = "observed"
    else:
        ap.error("use --demo, or --csv and --stations")

    val = None
    if a.demo and not a.skip_validation:
        print(f"Falsification + calibration: {a.cal_episodes} calibration + {a.eval_episodes} held-out synthetic episodes...")
        val = run_validation(a.cal_episodes, a.eval_episodes)
        json.dump(val, open(os.path.join(a.out, "validation.json"), "w"), indent=1)
    elif os.path.exists(os.path.join(a.out, "validation.json")):
        val = json.load(open(os.path.join(a.out, "validation.json")))
    t0 = time.time(); print("Fitting hierarchical receptor model (NUTS)...")
    r = run_inference(df, st, seed=a.seed)
    res = clean(r); res["data_source"] = source
    if truth is not None:
        tm = truth_means(truth, r["_w"])
        res["truth_mean_ugm3"] = dict(zip(["traffic", "industry", "dust", "biomass", "background"], [float(x) for x in tm]))
        res["truth_hourly_total"] = (truth["contrib"].sum(0) * r["_w"][:, None]).sum(0).round(1).tolist()
    print(f"  done in {time.time() - t0:.0f}s  rhat={r['sampler']['max_rhat']:.3f}  divergences={r['sampler']['divergences']}")
    json.dump(res, open(os.path.join(a.out, "results.json"), "w"), indent=1)

    build_dashboard(a.out, res, val)
    print(f"Wrote {a.out}/results.json, validation.json, dashboard.html")


if __name__ == "__main__":
    main()
