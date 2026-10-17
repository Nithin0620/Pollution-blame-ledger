"""Tracer-based source fingerprinting: turn raw observations into unit-mean source proxies.

Each proxy X_k is normalised to mean 1 per station over the episode. The model then subtracts a learned
baseline fraction a_k and rescales, so theta_{k,s} is the *episode-mean contribution of source k at station s (ug/m3)*.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import SOURCES

REQUIRED = ["datetime", "station", "pm25", "pm10", "no2", "so2", "co", "pblh_m", "wind_ms", "wind_dir_deg", "frp_footprint"]


def _excess(a, q=5):
    """Subtract each station's low-percentile baseline (urban background), clip at 0."""
    base = np.percentile(a, q, axis=1, keepdims=True)
    return np.clip(a - base, 0, None)


def _unit_mean(a):
    m = a.mean(axis=1, keepdims=True)
    return a / np.where(m == 0, 1, m)


def build(df: pd.DataFrame, stations: pd.DataFrame):
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"input is missing columns: {missing}")
    names = list(stations.station)
    piv = lambda col: np.vstack([df[df.station == n].sort_values("datetime")[col].to_numpy() for n in names])
    pm25, pm10, no2, so2, co = (piv(c) for c in ["pm25", "pm10", "no2", "so2", "co"])
    pblh, wind, foot = (piv(c)[0] for c in ["pblh_m", "wind_ms", "frp_footprint"])  # airshed-level met/fire
    times = np.sort(df.datetime.unique())

    vent = wind * pblh
    vinv = np.clip(np.median(vent) / vent, 0.2, 6.0)  # ventilation coefficient

    # Raw tracers, unit-mean. Their non-source baseline (urban/regional background) is learned in the model (a_k).
    x_traffic = _unit_mean(0.5 * (_unit_mean(co) + _unit_mean(no2)))                     # CO + NO2
    x_industry = _unit_mean(so2)                                                         # SO2
    x_dust = _unit_mean(np.clip(pm10 - pm25, 0, None))                                   # PM10 - PM2.5 coarse fraction
    x_bio = _unit_mean(np.tile(foot * vinv, (len(names), 1)))                            # wind-advected FRP x 1/ventilation
    X = np.stack([x_traffic, x_industry, x_dust, x_bio])
    w = stations.pop_m.to_numpy(float)
    w = w / w.sum()
    return {"X": X, "y": pm25, "w": w, "pop_m": stations.pop_m.to_numpy(float), "stations": names,
            "times": [str(t)[:16] for t in times], "vinv": vinv}
