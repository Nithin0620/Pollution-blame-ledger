"""Offline tests for ingestion using fabricated CPCB / FIRMS / met fixtures (no network)."""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ledger.ingest import load_cpcb, frp_footprint, assemble
from ledger.features import build


def _fixtures(tmp_path, days=3):
    rng = np.random.default_rng(0)
    t = pd.date_range("2025-11-01", periods=days * 24, freq="h")
    names = ["Anand Vihar", "RK Puram"]
    for n in names:
        pd.DataFrame({"From Date": t.strftime("%d-%m-%Y %H:%M"), "To Date": t.strftime("%d-%m-%Y %H:%M"),
                      "PM2.5 (ug/m3)": rng.uniform(80, 300, len(t)), "PM10 (ug/m3)": rng.uniform(150, 400, len(t)),
                      "NO2 (ug/m3)": rng.uniform(20, 90, len(t)), "SO2 (ug/m3)": rng.uniform(3, 15, len(t)),
                      "CO (mg/m3)": rng.uniform(0.5, 3, len(t))}).to_csv(tmp_path / f"{n}.csv", index=False)
    firms = pd.DataFrame({"latitude": rng.uniform(29, 31.5, 60), "longitude": rng.uniform(74, 76.5, 60),
                          "acq_date": rng.choice(["2025-11-01", "2025-11-02", "2025-11-03"], 60), "acq_time": 800, "frp": rng.uniform(5, 40, 60),
                          "confidence": "n"})
    firms.to_csv(tmp_path / "firms.csv", index=False)
    met = pd.DataFrame({"datetime": t, "wind_ms": 2.0, "wind_dir_deg": 310.0, "pblh_m": 400 + 600 * (t.hour.isin(range(10, 17)))})
    st = pd.DataFrame({"station": names, "lat": [28.6, 28.5], "lon": [77.3, 77.2], "pop_m": [5.0, 5.0]})
    return names, met, st


def test_end_to_end_schema(tmp_path):
    names, met, st = _fixtures(tmp_path)
    cp = load_cpcb(str(tmp_path / "Anand Vihar.csv"))
    assert {"pm25", "pm10", "no2", "so2", "co", "station", "datetime"} <= set(cp.columns)
    cp = pd.concat([load_cpcb(str(tmp_path / f"{n}.csv")) for n in names])
    fp = frp_footprint(str(tmp_path / "firms.csv"), met)
    assert (fp >= 0).all() and fp.sum() > 0
    obs, st2 = assemble(cp, st, met, fp)
    f = build(obs, st2)                         # the model's own feature builder accepts it
    assert f["X"].shape == (4, 2, 72)


def test_calibration_factor():
    from ledger.calibration import conformal_k
    assert conformal_k([1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1] * 10) == 1.0
    assert conformal_k([5] * 12, [1] * 12) == 5.0
