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
from ledger.baselines import run_baselines, run_shift_test


def clean(r):
    return {k: v for k, v in r.items() if not k.startswith("_")}


def collect_datasets(out):
    """Every dataset the dashboard can show: the synthetic demo plus any real datasets in outputs/datasets/."""
    ds = []
    rp = os.path.join(out, "results.json")
    if os.path.exists(rp):
        ds.append({"id": "demo", "name": "Synthetic demo (known truth)", "kind": "synthetic", "results": json.load(open(rp))})
    dd = os.path.join(out, "datasets")
    if os.path.isdir(dd):
        order = {"real_before": 0, "real_peak": 1, "real_after": 2}
        for f in sorted(os.listdir(dd), key=lambda x: order.get(x[:-5], 9)):
            if f.endswith(".json"):
                j = json.load(open(os.path.join(dd, f)))
                ds.append({"id": f[:-5], "name": j.pop("_name", f[:-5]), "kind": "real", "results": j})
    return ds


def build_dashboard(out, validation, name="dashboard.html"):
    tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard", "template.html"), encoding="utf-8").read()
    payload = json.dumps({"datasets": collect_datasets(out), "validation": validation})
    open(os.path.join(out, name), "w", encoding="utf-8").write(tpl.replace("/*__DATA__*/null", payload))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--csv"); ap.add_argument("--stations")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--cal-episodes", type=int, default=12)
    ap.add_argument("--eval-episodes", type=int, default=8)
    ap.add_argument("--skip-validation", action="store_true")
    ap.add_argument("--real", action="store_true", help="real-data checks: Dwarka Sec-8 CPCB + NASA FIRMS (data/)")
    ap.add_argument("--out", default="outputs")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    if a.real:
        from ledger.realcheck import run_real_checks
        print("Real-data run: six Delhi stations + NASA FIRMS, autumn 2018 (3 windows, ~4 min)...")
        chk, eps = run_real_checks("data/firms_viirs_punjab_haryana_daily_2018.csv")
        json.dump(chk, open(os.path.join(a.out, "real_checks.json"), "w"), indent=1)
        os.makedirs(os.path.join(a.out, "datasets"), exist_ok=True)
        names = {"before": "Delhi, 6 stations: before burning (20 Sep - 4 Oct 2018)", "peak": "Delhi, 6 stations: burning peak (28 Oct - 11 Nov 2018)",
                 "after": "Delhi, 6 stations: after burning (26 Nov - 10 Dec 2018)"}
        for k, r in eps.items():
            res = clean(r); res["data_source"] = "observed"; res["_name"] = names[k]
            res["data_note"] = f"{names[k]}. Six CPCB/DPCC stations + NASA FIRMS. Population weights and baseline death rate are placeholders."
            json.dump(res, open(os.path.join(a.out, "datasets", f"real_{k}.json"), "w"))
        vpath = os.path.join(a.out, "validation.json")
        val = json.load(open(vpath)) if os.path.exists(vpath) else {}
        val["real_checks"] = chk; json.dump(val, open(vpath, "w"), indent=1)
        build_dashboard(a.out, val)
        print("Wrote real_checks.json, datasets/real_*.json and the combined dashboard.html")
        return
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
    if val is not None and a.demo:
        if "baselines" not in val:
            print("Scoring baselines (NNLS, fixed published split) on the held-out episodes...")
            val["baselines"] = run_baselines(val)
        if "shift_test" not in val and not a.skip_validation:
            print("Shifted-event stress test (source mix changed, truth known)...")
            val["shift_test"] = run_shift_test(val["calibration"])
        json.dump(val, open(os.path.join(a.out, "validation.json"), "w"), indent=1)
    t0 = time.time(); print("Fitting hierarchical receptor model (NUTS)...")
    r = run_inference(df, st, seed=a.seed)
    res = clean(r); res["data_source"] = source
    if truth is not None:
        tm = truth_means(truth, r["_w"])
        res["truth_mean_ugm3"] = dict(zip(["traffic", "industry", "dust", "biomass", "background"], [float(x) for x in tm]))
        res["truth_hourly_total"] = (truth["contrib"].sum(0) * r["_w"][:, None]).sum(0).round(1).tolist()
    print(f"  done in {time.time() - t0:.0f}s  rhat={r['sampler']['max_rhat']:.3f}  divergences={r['sampler']['divergences']}")
    json.dump(res, open(os.path.join(a.out, "results.json"), "w"), indent=1)

    build_dashboard(a.out, val)
    print(f"Wrote {a.out}/results.json, validation.json, dashboard.html")


if __name__ == "__main__":
    main()
