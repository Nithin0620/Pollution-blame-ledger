"""Synthetic Delhi episode generator with KNOWN ground-truth source contributions.

Why this exists: real CPCB/FIRMS/ERA5 downloads need network access and credentials,
and attribution can only be *falsified* when the truth is known. The generator writes
the same CSV schema the real-data loader expects, so real data drops in unchanged.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import SOURCES

# Approximate station coordinates; `pop_m` is the (placeholder) population each station represents, in millions.
STATIONS = pd.DataFrame([
    # name,          lat,     lon,    pop_m, traffic, industry, dust, biomass  (relative susceptibility)
    ("Anand Vihar", 28.6469, 77.3158, 5.2, 1.5, 0.7, 1.4, 1.0),
    ("RK Puram",    28.5633, 77.1869, 5.0, 1.0, 0.5, 0.8, 0.9),
    ("ITO",         28.6286, 77.2410, 6.1, 1.6, 0.6, 1.1, 0.9),
    ("Rohini",      28.7325, 77.1170, 6.4, 0.9, 1.1, 0.9, 1.3),
    ("Dwarka",      28.5921, 77.0460, 5.6, 0.8, 0.6, 1.0, 1.1),
    ("Wazirpur",    28.6996, 77.1650, 4.7, 1.0, 1.9, 1.0, 1.1),
], columns=["station", "lat", "lon", "pop_m", "w_traffic", "w_industry", "w_dust", "w_biomass"])

# Mean contribution (ug/m3) per source at a susceptibility-1 station over the episode
BASE_MEAN = {"traffic": 34.0, "industry": 14.0, "dust": 22.0, "biomass": 48.0}


def _gauss(x, m, s):
    return np.exp(-0.5 * ((x - m) / s) ** 2)


def simulate(seed: int = 0, days: int = 10, scale: dict | None = None, start="2025-11-01"):
    """Return (df, stations, truth). `scale` multiplies a source's true contribution (plume injection)."""
    rng = np.random.default_rng(seed)
    scale = scale or {}
    T = days * 24
    t = np.arange(T)
    hour = t % 24
    day = t // 24
    S = len(STATIONS)

    # ---- meteorology -------------------------------------------------------------
    stag = np.clip(0.75 + np.cumsum(rng.normal(0, 0.12, days)) * 0.5, 0.35, 1.4)  # stagnation factor per day
    pblh = (180 + 950 * np.clip(np.sin(np.pi * (hour - 7) / 10), 0, None)) * stag[day]
    pblh = np.clip(pblh * rng.lognormal(0, 0.07, T), 90, None)
    wind = np.clip((0.6 + 1.6 * stag[day] * (0.5 + 0.5 * np.sin(np.pi * (hour - 5) / 14))) * rng.lognormal(0, 0.15, T), 0.3, None)
    wdir = (315 + rng.normal(0, 35, days)[day] + rng.normal(0, 15, T)) % 360
    vent = wind * pblh
    vinv = np.clip(np.median(vent) / vent, 0.2, 6.0)  # 1/ventilation, normalised

    # ---- emission shapes ---------------------------------------------------------
    e_traffic = 0.35 + 0.65 * (_gauss(hour, 8.5, 1.7) + 0.9 * _gauss(hour, 19, 2.2))
    e_industry = 0.85 + 0.15 * np.cumsum(rng.normal(0, 0.05, T)) / np.sqrt(np.arange(1, T + 1)) * 4
    e_dust = (0.15 + 0.85 * _gauss(hour, 14, 3.8)) * (0.6 + 0.4 * wind / wind.mean())
    # fires: seasonal pulse across the episode, afternoon-peaked, ~11 h transport lag from Punjab/Haryana
    pulse = np.exp(-0.5 * ((np.arange(days) - rng.uniform(3.5, 6.5)) / 2.2) ** 2) * rng.lognormal(0, 0.25, days)
    frp = pulse[day] * (0.25 + 0.75 * _gauss(hour, 14.5, 3.5))
    lag = 11
    frp_arrive = np.roll(frp, lag); frp_arrive[:lag] = frp[:lag].mean()
    wind_w = 0.15 + 0.85 * np.clip(np.cos(np.deg2rad(wdir - 315)), 0, None) ** 2
    e_bio = frp_arrive * wind_w

    shapes = {"traffic": e_traffic * vinv, "industry": e_industry * vinv,
              "dust": e_dust * vinv, "biomass": e_bio * vinv}
    for k in SOURCES:  # normalise to unit mean so BASE_MEAN is the episode-mean contribution
        shapes[k] = shapes[k] / shapes[k].mean()

    # ---- ground-truth contributions [K,S,T] -------------------------------------
    contrib = np.zeros((len(SOURCES), S, T))
    for i, k in enumerate(SOURCES):
        beta = BASE_MEAN[k] * STATIONS[f"w_{k}"].values * rng.lognormal(0, 0.1, S) * scale.get(k, 1.0)
        local_noise = rng.lognormal(0, 0.12, (S, T))
        contrib[i] = beta[:, None] * shapes[k][None, :] * local_noise

    # regional background: day-scale random walk, linearly interpolated to hours
    bg_d = 38 * np.exp(np.cumsum(rng.normal(0, 0.12, days + 1)))
    background = np.interp(t, np.arange(days + 1) * 24, bg_d)

    pm25 = np.clip(background[None, :] + contrib.sum(0) + rng.normal(0, 7, (S, T)), 5, None)

    tr, ind, du, bio = contrib
    ln = lambda s: rng.lognormal(0, 0.08, (S, T)) if s else 1
    co = (0.5 + 0.035 * tr + 0.012 * bio) * ln(1)                      # mg/m3 ; biomass leaks into CO (realistic collinearity)
    no2 = (12 + 0.9 * tr + 0.2 * ind) * ln(1)
    so2 = (4 + 0.35 * ind + 0.03 * bio) * ln(1)
    pm10 = pm25 + (25 + 1.8 * du) * ln(1)
    # observed FRP footprint: window-averaged (lag unknown to the analyst) x wind weight, with cloud-gap noise
    foot = np.array([frp[max(0, i - 18): max(1, i - 5)].mean() if i > 5 else frp[:6].mean() for i in range(T)]) * wind_w
    foot = foot * rng.lognormal(0, 0.15, T)

    ts = pd.date_range(start, periods=T, freq="h")
    rows = []
    for s, name in enumerate(STATIONS.station):
        rows.append(pd.DataFrame({
            "datetime": ts, "station": name, "pm25": pm25[s], "pm10": pm10[s], "no2": no2[s],
            "so2": so2[s], "co": co[s], "pblh_m": pblh, "wind_ms": wind, "wind_dir_deg": wdir,
            "frp_footprint": foot,
        }))
    df = pd.concat(rows, ignore_index=True)
    truth = {"contrib": contrib, "background": background, "sources": SOURCES}
    return df, STATIONS.copy(), truth
