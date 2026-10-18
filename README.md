# Pollution Blame Ledger

> **Research prototype - read before citing any number.** All data in this repo is **synthetic** (simulated Delhi-like observations with known ground truth). Health figures use **placeholder** concentration-response, baseline-mortality and population values. Individual source splits are only reliable after the validation-derived interval widening described below; nothing here is a claim about real Delhi air or real deaths.

Probabilistic source apportionment of Delhi PM2.5 with uncertainty-quantified health burden (deaths and hospital admissions) and an explicit statement of what the data cannot separate.

## Quick start
```
pip install -r requirements.txt
python run.py --demo                    # ~10 min: 12 calibration + 8 held-out episodes, plume injection, dashboard
python run.py --demo --skip-validation  # ~30 s: reuse saved calibration + validation
python -m pytest tests                  # offline tests (generator, features, health, diagnostics, ingestion, calibration)
```
Open `outputs/dashboard.html` (self-contained, no server).

## What it does (maps to the problem statement)
| Spec step | Code |
|---|---|
| 1 Multi-modal data fusion | `ledger/ingest.py` (CPCB CSVs + Open-Meteo/ERA5 met + NASA FIRMS fires), `ledger/features.py` |
| 2 Tracer fingerprinting | CO+NO2 traffic, SO2 industry, PM10-PM2.5 dust, wind-advected FRP x 1/ventilation biomass |
| 3 Hierarchical Bayesian receptor model (NUTS) | `ledger/model.py`: non-negative partially pooled source terms, learned tracer baselines, tracer cross-talk unmixing, proxy-mismatch gain, daily background random walk; `ledger/diagnostics.py` flags trade-off pairs |
| 4 Health-burden propagation | `ledger/health.py`: GEMM mortality + short-term admissions, counterfactual removal (50% / 100%), Monte Carlo over CRF and baseline-rate uncertainty |
| 5 Falsification | `ledger/validate.py`: synthetic ground-truth recovery, held-out calibration, coverage, plume injection; `ledger/calibration.py` |

## Real data
```
python -m ledger.ingest --cpcb data/cpcb/ --firms data/firms_viirs.csv --stations data/stations.csv \
    --start 2025-11-01 --end 2025-11-10 --out data/episode
python run.py --csv data/episode/observations.csv --stations data/episode/stations.csv
```
`stations.csv`: `station, lat, lon, pop_m` (names must match the CPCB file names/columns). Ingestion is unit-tested on fabricated fixtures only; the Open-Meteo fetch and real CPCB/FIRMS exports have **not** been run in the build environment (no internet). Expect to adjust column matching on first contact with real files.

## Validation results (synthetic, 12 calibration + 8 held-out episodes)
- Raw posterior intervals are over-confident (0-25% coverage for most sources). Dust is recovered well (8% median error); the traffic+biomass **sum** is recovered well (8%); individual traffic / industry / biomass / background splits are biased (20-55% median error).
- Interval widening learned on the calibration episodes gives 75-100% coverage on held-out episodes. This makes the ledger honest, not more precise.
- Sources whose widening factor is >= 2.5 can no longer be labelled "identified".
- Plume injection: doubling traffic or biomass is detected; for biomass the truth still falls outside the calibrated interval.

## Known limitations / next steps
1. Calibration comes from synthetic episodes; re-calibrate on real episodes with independent ground truth (receptor-model campaigns, speciation data).
2. Replace placeholder parameters: age-specific GEMM, Delhi SRS/GBD baseline rates, WorldPop populations, admissions CRF.
3. Explicit source-profile (PMF/CMB-style) mixing and Lagrangian back-trajectories (HYSPLIT) to improve separation of traffic vs biomass.
4. Sentinel-2 land-cover change and OSM road/industrial geometries are not yet used.
5. Leave-one-episode-out and triangulation against published apportionment studies on real data.
