"""INDEPENDENT, deliberately misspecified generator for out-of-model validation.

The main generator (synth.py) shares its structure with the receptor model, so passing it proves little.
This one is built to BREAK the model's assumptions, in ways documented in the literature on receptor modelling:
  * secondary aerosol: formed nonlinearly from NO2/SO2/biomass precursors and lagged; the model has no such source
  * tracers: NO2 saturates with traffic (sqrt), CO has a large non-traffic domestic-burning component, SO2 has a
    traffic-fuel component, PM10-PM2.5 has a humidity-driven component unrelated to dust
  * fire plumes arrive as discrete passes with a random 5-16 h lag per day (model assumes a smooth proxy)
  * weekday/weekend traffic cycle, industrial step shutdowns, resuspension that scales with wind^2
  * heavy-tailed (Student-t) noise, per-station tracer drift, and gaps filled by interpolation
Same CSV schema as synth.py. Truth: `contrib` = PRIMARY source contributions; `background` = regional + secondary.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import SOURCES
from .synth import STATIONS, BASE_MEAN


def _g(x, m, s):
    return np.exp(-0.5 * ((x - m) / s) ** 2)


def simulate_alt(seed: int = 0, days: int = 10, scale: dict | None = None, start="2025-11-01"):
    rng = np.random.default_rng(seed)
    scale = scale or {}
    T = days * 24; t = np.arange(T); hour = t % 24; day = t // 24; S = len(STATIONS)
    dow = (day + rng.integers(0, 7)) % 7
    stag = np.clip(0.7 + np.cumsum(rng.normal(0, 0.18, days)) * 0.5, 0.3, 1.5)
    pblh = np.clip((150 + 1100 * np.clip(np.sin(np.pi * (hour - 6.5) / 11), 0, None)) * stag[day] * rng.lognormal(0, 0.12, T), 80, None)
    wind = np.clip((0.5 + 2.0 * stag[day] * (0.4 + 0.6 * np.sin(np.pi * (hour - 4) / 15))) * rng.lognormal(0, 0.25, T), 0.25, None)
    wdir = (300 + rng.normal(0, 50, days)[day] + rng.normal(0, 25, T)) % 360
    vinv = np.clip(np.median(wind * pblh) / (wind * pblh), 0.2, 6.0)
    rh = np.clip(55 + 30 * np.cos(np.pi * (hour - 5) / 12) * 0.5 + rng.normal(0, 8, days)[day], 25, 98)

    weekend = (dow >= 5)
    e_tr = (0.3 + 0.7 * (_g(hour, 9, 2.0) + 0.7 * _g(hour, 18.5, 2.6))) * np.where(weekend, 0.75, 1.0)
    shut = np.ones(T)
    for _ in range(rng.integers(1, 3)):
        a = rng.integers(0, T - 30); shut[a:a + rng.integers(12, 40)] = rng.uniform(0.3, 0.6)
    e_in = shut * (0.9 + 0.1 * np.sin(t / 9.0))
    e_du = (0.1 + 0.9 * _g(hour, 13, 4.5)) * (wind / wind.mean()) ** 2 * np.where(rng.random(days) < 0.3, 0.4, 1.0)[day]
    # fire passes: each day one or two gamma-shaped passes, lag 5-16 h
    fire = np.zeros(T)
    pulse = np.exp(-0.5 * ((np.arange(days) - rng.uniform(3, 7)) / 1.8) ** 2) * rng.lognormal(0, 0.4, days)
    for d in range(days):
        for _ in range(1 + rng.integers(0, 2)):
            c = d * 24 + 14 + rng.integers(5, 17); w = rng.uniform(2, 5)
            fire += pulse[d] * rng.uniform(0.4, 1.0) * _g(t, c, w)
    wind_w = 0.1 + 0.9 * np.clip(np.cos(np.deg2rad(wdir - 305)), 0, None) ** 1.5
    e_bi = (fire + 0.03) * wind_w

    shapes = {"traffic": e_tr * vinv, "industry": e_in * vinv, "dust": e_du * vinv, "biomass": e_bi * vinv}
    shapes = {k: v / v.mean() for k, v in shapes.items()}
    contrib = np.zeros((4, S, T))
    for i, k in enumerate(SOURCES):
        beta = BASE_MEAN[k] * STATIONS[f"w_{k}"].values * rng.lognormal(0, 0.25, S) * scale.get(k, 1.0) * 0.9
        contrib[i] = beta[:, None] * shapes[k][None, :] * rng.lognormal(0, 0.2, (S, T))
    tr, ind, du, bio = contrib

    bg_d = 30 * np.exp(np.cumsum(rng.normal(0, 0.15, days + 1)))
    regional = np.interp(t, np.arange(days + 1) * 24, bg_d)
    # secondary: slow nonlinear conversion of precursors (hours-long lag), more at high humidity
    prec = (tr.mean(0) * 0.4 + ind.mean(0) * 1.2 + bio.mean(0) * 0.5)
    k_ = np.exp(-t / 1e9)
    sec = np.convolve(prec, np.exp(-np.arange(0, 36) / 10.0) / 10.0, mode="full")[:T] * (0.5 + rh / 100) * 0.9
    background = regional + sec

    pm25 = np.clip(background[None, :] + contrib.sum(0) + 6 * rng.standard_t(4, (S, T)), 5, None)
    drift = lambda: np.exp(np.cumsum(rng.normal(0, 0.004, (S, T)), axis=1))
    ln = lambda s: rng.lognormal(0, s, (S, T))
    co = (0.5 + 0.03 * np.sqrt(tr + 1) * 4 + 0.010 * bio + 0.9 * (0.5 + 0.5 * _g(hour, 21, 3))[None, :]) * ln(0.1) * drift()
    no2 = (10 + 5.0 * np.sqrt(tr + 1) + 0.15 * ind) * ln(0.1) * drift()
    so2 = (3.5 + 0.30 * ind + 0.03 * tr + 0.02 * bio) * ln(0.12) * drift()
    pm10 = pm25 + (20 + 1.5 * du + 0.25 * rh[None, :]) * ln(0.12) * drift()
    foot = np.array([fire[max(0, i - 20): max(1, i - 3)].mean() for i in range(T)]) * wind_w * rng.lognormal(0, 0.3, T)

    frames = []
    ts = pd.date_range(start, periods=T, freq="h")
    for s, name in enumerate(STATIONS.station):
        d = pd.DataFrame({"datetime": ts, "station": name, "pm25": pm25[s], "pm10": pm10[s], "no2": no2[s],
                          "so2": so2[s], "co": co[s], "pblh_m": pblh, "wind_ms": wind, "wind_dir_deg": wdir,
                          "frp_footprint": foot})
        for col in ["pm25", "pm10", "no2", "so2", "co"]:      # sensor gaps, repaired by linear interpolation
            for _ in range(rng.integers(0, 3)):
                a = rng.integers(0, T - 8); d.loc[a:a + rng.integers(2, 8), col] = np.nan
            d[col] = d[col].interpolate(limit_direction="both")
        frames.append(d)
    return pd.concat(frames, ignore_index=True), STATIONS.copy(), {"contrib": contrib, "background": background, "sources": SOURCES}
