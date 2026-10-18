"""Adapter: real single-station CPCB-style hourly file + NASA FIRMS fire detections -> model schema.

Fire input: daily FRP series (see data/firms_viirs_punjab_haryana_daily_2018.csv).
Input file columns used (CPCB/CAAQMS export format): PM2.5, PM10, NO2, SO2, CO, WS, WD, AT (deg C), SR (W/m2),
and year, month, day, hour.  
Documented approximations (replace with better inputs when available):
  * pblh_m is a PROXY from solar radiation (no ERA5 boundary-layer height in the file).  It only needs to get the
    diurnal/seasonal ventilation SHAPE right: the model uses it through unit-mean proxies.
  * frp_footprint = mean regional daily FRP over the preceding 5-18 h x a north-westerly wind weight, the same
    construction the synthetic episodes use.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

COLS = {"PM2.5": "pm25", "PM10": "pm10", "NO2": "no2", "SO2": "so2", "CO": "co"}


def load_cpcb(path):
    d = pd.read_csv(path, index_col=0)
    d["datetime"] = pd.to_datetime(dict(year=d.year.astype(int), month=d.month.astype(int), day=d.day.astype(int), hour=d.hour.astype(int)))
    return d.sort_values("datetime").reset_index(drop=True)


def pblh_proxy(sr, at=None):
    sr_s = pd.Series(sr).rolling(3, min_periods=1, center=True).mean().to_numpy()
    return np.clip(120 + 2.2 * sr_s, 120, 2500)


def load_fire_daily(path):
    f = pd.read_csv(path, comment="#", parse_dates=["date"])
    return f.set_index("date").frp_mw


def fire_hourly(daily, times, lag_window=(5, 18)):
    """Regional fire power per hour from daily FRP totals (IST day): afternoon-weighted diurnal shape, then the
    mean over the preceding 5-18 h (transport lag from Punjab/Haryana)."""
    idx = pd.DatetimeIndex(times)
    day = idx.floor("D")
    cal = daily.reindex(pd.date_range(day.min() - pd.Timedelta(days=2), day.max(), freq="D")).fillna(0.0)
    hourly = cal.reindex(day).to_numpy()
    hh = idx.hour.to_numpy()
    shape = 0.25 + 0.75 * np.exp(-0.5 * ((hh - 14.5) / 3.5) ** 2)
    a, b = lag_window
    return pd.Series(hourly * shape).rolling(b - a + 1, min_periods=1).mean().shift(a).bfill().to_numpy()


def to_episode(cpcb, fire_daily, start, end, station="Dwarka Sec-8", lat=28.5921, lon=77.0460, pop_m=5.6):
    d = cpcb[(cpcb.datetime >= start) & (cpcb.datetime < end)].copy()
    d = d.dropna(subset=list(COLS))
    full = pd.date_range(start, end, freq="h", inclusive="left")
    d = d.set_index("datetime").reindex(full).interpolate(limit_direction="both")
    wd = d.WD.to_numpy(); wind_w = 0.15 + 0.85 * np.clip(np.cos(np.deg2rad(wd - 315)), 0, None) ** 2
    foot = fire_hourly(fire_daily, full) * wind_w
    out = pd.DataFrame({"datetime": full, "station": station, **{v: d[k].to_numpy() for k, v in COLS.items()},
                        "pblh_m": pblh_proxy(d.SR.to_numpy(), d.AT.to_numpy()), "wind_ms": np.clip(d.WS.to_numpy(), 0.3, None),
                        "wind_dir_deg": wd, "frp_footprint": foot})
    st = pd.DataFrame([(station, lat, lon, pop_m)], columns=["station", "lat", "lon", "pop_m"])
    return out, st


# Six Delhi CPCB/DPCC stations supplied by the team (hourly, 1 Jun 2018 - 1 Oct 2019).
# Coordinates are approximate public station-listing values (display only; NOT used in inference).
# `pop_m` is a PLACEHOLDER: Delhi's ~20 M split equally, pending a real per-station catchment population.
STATIONS6 = [
    ("Ashok Vihar", "data/cpcb/ashok_vihar_hourly.csv", 28.6950, 77.1818),
    ("Dwarka Sec-8", "data/cpcb/dwarka_sec8_hourly.csv", 28.5710, 77.0719),
    ("Najafgarh", "data/cpcb/najafgarh_hourly.csv", 28.5700, 76.9800),
    ("Okhla Ph-2", "data/cpcb/okhla_hourly.csv", 28.5308, 77.2711),
    ("Nehru Nagar", "data/cpcb/nehru_nagar_hourly.csv", 28.5678, 77.2507),
    ("Major Dhyan Chand Stadium", "data/cpcb/dc_stadium_hourly.csv", 28.6120, 77.2373),
]
DELHI_POP_M_PLACEHOLDER = 20.0


def to_episode_multi(fire_daily, start, end, base=".", stations=STATIONS6):
    """Combine all stations into one episode. Airshed-level fields (boundary-layer proxy, wind, fire footprint)
    use the cross-station median so every station shares the same meteorology, as the model assumes."""
    import os
    per = []
    for name, path, lat, lon in stations:
        df, st = to_episode(load_cpcb(os.path.join(base, path)), fire_daily, start, end, station=name, lat=lat, lon=lon)
        per.append(df)
    air = ["pblh_m", "wind_ms", "wind_dir_deg", "frp_footprint"]
    med = {c: np.median(np.vstack([d[c].to_numpy() for d in per]), axis=0) for c in air}
    # wind direction is circular: take the median of the unit vectors instead
    rad = np.deg2rad(np.vstack([d["wind_dir_deg"].to_numpy() for d in per]))
    med["wind_dir_deg"] = np.rad2deg(np.arctan2(np.sin(rad).mean(0), np.cos(rad).mean(0))) % 360
    for d in per:
        for c in air:
            d[c] = med[c]
    st = pd.DataFrame([(n, la, lo, DELHI_POP_M_PLACEHOLDER / len(stations)) for n, _, la, lo in stations],
                      columns=["station", "lat", "lon", "pop_m"])
    return pd.concat(per, ignore_index=True), st
