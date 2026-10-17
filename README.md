# Pollution Blame Ledger — MVP

> **Research prototype - read before citing any number.** All data in this repo is **synthetic** (simulated Delhi-like observations with known ground truth). Health figures use **placeholder** concentration-response, baseline-mortality and population values. In validation, only dust and the traffic+biomass *sum* are recovered reliably; individual source splits are biased and their intervals over-confident. Nothing here is a claim about real Delhi air or real deaths.

Probabilistic source apportionment of Delhi PM2.5 with uncertainty-quantified health burden.

## Run
```
pip install -r requirements.txt
python run.py --demo                    # synthetic episode + validation + dashboard (~12 min; add --skip-validation for ~1 min)
python run.py --csv obs.csv --stations stations.csv   # real data
python -m pytest tests
```
Open `outputs/dashboard.html`.

## Pipeline (maps to the spec)
| Spec step | Code |
|---|---|
| 1 Data fusion | `ledger/features.py` (CSV schema below); `ledger/synth.py` generates schema-identical synthetic data |
| 2 Tracer fingerprinting | `features.py`: CO+NO2 traffic, SO2 industry, PM10-PM2.5 dust, FRP footprint x 1/ventilation biomass |
| 3 Hierarchical Bayesian receptor (NUTS) | `ledger/model.py`; identifiability in `ledger/diagnostics.py` |
| 4 Health burden | `ledger/health.py` (GEMM CRF, counterfactual removal, Monte Carlo) |
| 5 Falsification | `ledger/validate.py` (synthetic truth recovery, coverage, plume injection) |

Input schema: observations `datetime, station, pm25, pm10, no2, so2, co, pblh_m, wind_ms, wind_dir_deg, frp_footprint`; stations `station, lat, lon, pop_m`.

## Honest status (first validation, 8 synthetic episodes)
- Recovered well: dust (88% CI coverage) and the **traffic + biomass sum** (3% median error); PM2.5 predictive coverage 93%.
- Not yet: individual traffic / biomass / industry / background splits are biased with over-confident intervals (0% coverage). Traffic and biomass share the night-time ventilation signal, so the dashboard reports them as a flagged pair.
- Plume injection: doubling traffic and biomass is detected; biomass truth falls outside the CI.

## Next steps
1. Fix over-confidence (explicit source profiles / PMF-style mixing, wider structural ensemble).
2. Real data: CPCB, ERA5 PBLH, FIRMS + HYSPLIT footprints, WorldPop.
3. Age-specific GEMM, Delhi baseline rates, morbidity.
4. Leave-one-episode-out on real episodes; triangulate with published apportionment studies.

Placeholders (GEMM pooled params, baseline mortality, populations) are marked in `health.py` and the dashboard.
