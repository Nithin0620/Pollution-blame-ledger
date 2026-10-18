"""Real-data ingestion: CPCB station exports + Open-Meteo/ERA5 meteorology + NASA FIRMS fires -> model schema.

Offline-testable pieces (no network): `load_cpcb`, `frp_footprint`, `assemble`.
Network pieces (`fetch_meteo`) must be run somewhere with internet; they could not be exercised in the build sandbox.

Typical use:
    python -m ledger.ingest --cpcb data/cpcb/ --firms data/firms_viirs.csv --stations data/stations.csv \
        --start 2025-11-01 --end 2025-11-10 --out data/episode_2025_11
    python run.py --csv data/episode_2025_11/observations.csv --stations data/episode_2025_11/stations.csv
"""
from __future__ import annotations
import argparse, glob, math, os, re
import numpy as np
import pandas as pd

DELHI = (28.61, 77.21)
PUNJAB_HARYANA_BOX = dict(lat=(28.4, 32.5), lon=(73.8, 77.6))      # rough crop-residue source region
POLLUTANT_PATTERNS = {
    "pm25": r"pm\s*2\.?5", "pm10": r"pm\s*10", "no2": r"\bno2\b", "so2": r"\bso2\b", "co": r"^co\b|\bco\s*\(",
}


def _match_col(cols, pat):
    for c in cols:
        if re.search(pat, c.lower()):
            return c
    return None


def load_cpcb(path, station=None, max_gap_h=3, max_missing=0.3):
    """Read CPCB CAAQMS-style CSV(s) (a file, or a directory with one file per station).

    Accepts a 'From Date'/'To Date'/'Timestamp'/'datetime' column and columns such as 'PM2.5 (ug/m3)', 'CO (mg/m3)'.
    A 'station' column is used if present, else the file name (without extension). Returns hourly long-format data.
    """
    files = sorted(glob.glob(os.path.join(path, "*.csv"))) if os.path.isdir(path) else [path]
    out = []
    for f in files:
        d = pd.read_csv(f)
        tcol = next((c for c in d.columns if re.search(r"from date|timestamp|datetime|^date", c.lower())), None)
        if tcol is None:
            raise ValueError(f"{f}: no timestamp column found in {list(d.columns)}")
        res = pd.DataFrame({"datetime": pd.to_datetime(d[tcol], dayfirst=True, errors="coerce")})
        for k, pat in POLLUTANT_PATTERNS.items():
            c = _match_col([x for x in d.columns if x != tcol], pat)
            res[k] = pd.to_numeric(d[c], errors="coerce") if c else np.nan
        scol = next((c for c in d.columns if c.lower() in ("station", "station name", "site")), None)
        res["station"] = d[scol].astype(str) if scol else (station or os.path.splitext(os.path.basename(f))[0])
        out.append(res.dropna(subset=["datetime"]))
    df = pd.concat(out, ignore_index=True)
    df["datetime"] = df["datetime"].dt.floor("h")
    for k in POLLUTANT_PATTERNS:
        df.loc[df[k] < 0, k] = np.nan                                  # sentinel / invalid
    parts, dropped = [], []
    for s, g in df.groupby("station"):
        g = g.groupby("datetime").mean(numeric_only=True)
        g = g.reindex(pd.date_range(g.index.min(), g.index.max(), freq="h"))
        if g[list(POLLUTANT_PATTERNS)].isna().mean().max() > max_missing:
            dropped.append(s); continue
        g = g.interpolate(limit=max_gap_h, limit_direction="both")
        g["station"] = s; g.index.name = "datetime"
        parts.append(g.reset_index())
    if dropped:
        print(f"[ingest] dropped stations with >{int(max_missing * 100)}% missing: {dropped}")
    return pd.concat(parts, ignore_index=True)


def fetch_meteo(start, end, lat=DELHI[0], lon=DELHI[1], hist_forecast=True):
    """Hourly wind speed (m/s), direction and boundary-layer height from Open-Meteo. NEEDS INTERNET.

    Uses the historical-forecast endpoint because it exposes boundary_layer_height; swap to ERA5 (CDS API) for a
    fully reanalysis-based record. Column names follow the model schema. Timestamps are requested in IST.
    """
    import requests
    base = "https://historical-forecast-api.open-meteo.com/v1/forecast" if hist_forecast else "https://archive-api.open-meteo.com/v1/archive"
    r = requests.get(base, params=dict(latitude=lat, longitude=lon, start_date=start, end_date=end, timezone="Asia/Kolkata",
                                       hourly="wind_speed_10m,wind_direction_10m,boundary_layer_height", wind_speed_unit="ms"), timeout=60)
    r.raise_for_status()
    h = r.json()["hourly"]
    m = pd.DataFrame({"datetime": pd.to_datetime(h["time"]), "wind_ms": h["wind_speed_10m"],
                      "wind_dir_deg": h["wind_direction_10m"], "pblh_m": h["boundary_layer_height"]})
    if m["pblh_m"].isna().all():
        raise RuntimeError("boundary_layer_height unavailable; supply ERA5 PBLH via the CDS API and pass it to assemble()")
    return m


def _bearing(lat1, lon1, lat2, lon2):
    p1, p2, dl = map(math.radians, (lat1, lat2, lon2 - lon1))
    x = math.sin(dl) * math.cos(p2); y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def frp_footprint(firms_csv, met, box=PUNJAB_HARYANA_BOX, window=(5, 18), min_conf=("n", "h", "nominal", "high")):
    """Hourly wind-advected fire-radiative-power footprint at Delhi from a FIRMS VIIRS CSV.

    1. Sum FRP of fire pixels inside the source box per IST day (VIIRS passes are ~01:30/13:30 local, so we use daily
       totals), distribute over the day with an afternoon-peaked burning profile.
    2. Average FRP over the preceding `window` hours (transport time from Punjab/Haryana is uncertain: 5-18 h).
    3. Weight by how much the wind blows from the source region toward Delhi: cos^2(angle), floor 0.15.
    """
    f = pd.read_csv(firms_csv)
    f = f[(f.latitude.between(*box["lat"])) & (f.longitude.between(*box["lon"]))]
    if "confidence" in f.columns:
        f = f[f["confidence"].astype(str).str.lower().isin([str(c) for c in min_conf]) | pd.to_numeric(f["confidence"], errors="coerce").ge(50)]
    t = pd.to_datetime(f.acq_date) + pd.to_timedelta(f.acq_time.astype(int).astype(str).str.zfill(4).str[:2].astype(int), unit="h") \
        + pd.to_timedelta(f.acq_time.astype(int).astype(str).str.zfill(4).str[2:].astype(int), unit="m") + pd.Timedelta(hours=5.5)
    daily = f.assign(day=t.dt.floor("D")).groupby("day").frp.sum()
    times = pd.to_datetime(met["datetime"]).reset_index(drop=True)
    day_frp = times.dt.floor("D").map(daily).fillna(0.0).to_numpy()
    hr = times.dt.hour.to_numpy()
    profile = 0.25 + 0.75 * np.exp(-0.5 * ((hr - 14.5) / 3.5) ** 2)
    frp = day_frp / 24 * profile / profile.mean()
    lo_w, hi_w = window
    avg = np.array([frp[max(0, i - hi_w): max(1, i - lo_w + 1)].mean() if i >= lo_w else frp[: lo_w + 1].mean() for i in range(len(frp))])
    cen = (np.mean(box["lat"]), np.mean(box["lon"]))
    brg = _bearing(DELHI[0], DELHI[1], *cen)              # direction FROM Delhi TO the source; wind must come FROM it
    wd = met["wind_dir_deg"].to_numpy()
    w = 0.15 + 0.85 * np.clip(np.cos(np.deg2rad(wd - brg)), 0, None) ** 2
    return pd.Series(avg * w, index=pd.to_datetime(met["datetime"]), name="frp_footprint")


def assemble(cpcb, stations, met, footprint):
    """Merge everything into the model's observation schema (inner-joined on hourly timestamps)."""
    m = met.copy(); m["datetime"] = pd.to_datetime(m["datetime"])
    m = m.merge(footprint.rename("frp_footprint").reset_index().rename(columns={"index": "datetime"}), on="datetime", how="left")
    d = cpcb[cpcb.station.isin(stations.station)].merge(m, on="datetime", how="inner")
    need = ["pm25", "pm10", "no2", "so2", "co", "pblh_m", "wind_ms", "wind_dir_deg", "frp_footprint"]
    d = d.dropna(subset=need)
    common = set.intersection(*[set(g.datetime) for _, g in d.groupby("station")])
    d = d[d.datetime.isin(common)].sort_values(["station", "datetime"])
    keep = [s for s in stations.station if s in set(d.station)]
    n = len(common) // 24 * 24
    first = sorted(common)[:n]                                   # model needs whole days
    d = d[d.datetime.isin(first)]
    return d[["datetime", "station"] + need], stations[stations.station.isin(keep)].reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cpcb", required=True); ap.add_argument("--firms", required=True)
    ap.add_argument("--stations", required=True, help="CSV: station, lat, lon, pop_m (match CPCB station names)")
    ap.add_argument("--start", required=True); ap.add_argument("--end", required=True)
    ap.add_argument("--met-csv", help="optional pre-downloaded met CSV (datetime, wind_ms, wind_dir_deg, pblh_m) instead of fetching")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    st = pd.read_csv(a.stations)
    cp = load_cpcb(a.cpcb)
    cp = cp[(cp.datetime >= a.start) & (cp.datetime < pd.Timestamp(a.end) + pd.Timedelta(days=1))]
    met = pd.read_csv(a.met_csv, parse_dates=["datetime"]) if a.met_csv else fetch_meteo(a.start, a.end)
    fp = frp_footprint(a.firms, met)
    obs, st2 = assemble(cp, st, met, fp)
    obs.to_csv(os.path.join(a.out, "observations.csv"), index=False); st2.to_csv(os.path.join(a.out, "stations.csv"), index=False)
    print(f"[ingest] {obs.station.nunique()} stations x {obs.datetime.nunique()} hours -> {a.out}")


if __name__ == "__main__":
    main()
