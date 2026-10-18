<div align="center">

# The Pollution Blame Ledger

**Probabilistic source apportionment of Delhi PM<sub>2.5</sub>, with uncertainty-quantified health burden and an explicit statement of what the data cannot separate.**

![Status](https://img.shields.io/badge/status-research%20prototype-orange)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Inference](https://img.shields.io/badge/inference-NumPyro%20%7C%20NUTS-6f42c1)
![Tests](https://img.shields.io/badge/tests-10%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

</div>

**Team Last Attempt.**

> **Research prototype. Read before citing any number.** The repository holds two kinds of data: a **simulated** demo episode with known ground truth (used to validate the method) and **real** hourly readings from six Delhi CPCB stations plus NASA fire detections for 2018. Real-data source shares have **no ground truth**. GEMM parameters are verified against the published release; baseline mortality, population weights and admissions values are still **placeholders**. Use the death figures to compare sources, not as absolute counts.

<p align="center">
  <img src="docs/screenshots/01-home.png" alt="Home page: what the Ledger does and where to start" width="900">
</p>

## Contents
[Research foundation](docs/RESEARCH.md) · [The problem](#the-problem) · [What the ledger does differently](#what-the-ledger-does-differently) · [Dashboard tour](#dashboard-tour) · [How it works](#how-it-works) · [Results](#results) · [Quick start](#quick-start) · [Real data](#real-data) · [Repository layout](#repository-layout) · [Limitations and roadmap](#limitations-and-roadmap)

## The problem
Delhi's PM<sub>2.5</sub> episodes are the superposition of co-varying emission streams (crop-residue burning, vehicles, construction dust, industry) modulated by meteorology. Attribution is an ill-posed inverse problem, so public debate runs on anecdote that cannot be falsified, and the health burden of each source is never quantified.

## What the ledger does differently
| | Typical dashboards | The Pollution Blame Ledger |
|---|---|---|
| Output | µg/m³ readings | Share, premature deaths and hospital admissions **per source** |
| Uncertainty | Rarely shown | 90% credible intervals on every figure, calibrated on held-out tests |
| Limits | Implicit | **Identifiability is a first-class output**: source pairs the data cannot separate are flagged and reported as a sum |
| Trust | Take our word | **Falsifiable**: synthetic plume injection and held-out episodes with known truth |
| Policy use | Descriptive | Counterfactual source removal (50% and 100% cuts) |

## Dashboard tour
One self-contained HTML file with four places, reachable from the top bar. A first-time visitor can follow them in order.

<table>
<tr>
<td width="50%"><b>1. Home: what is this?</b><br>A plain-language intro and four steps, then the datasets.<br><img src="docs/screenshots/01-home.png" alt="Home"></td>
<td width="50%"><b>2. Datasets</b><br>The simulated episode (known truth), three real Delhi windows from six CPCB stations, and an upload card.<br><img src="docs/screenshots/02-datasets.png" alt="Dataset cards"></td>
</tr>
<tr>
<td width="50%"><b>3. Dive in</b><br>Click a source for its share, deaths, and a plain-words trust label with test accuracy.<br><img src="docs/screenshots/03-analysis.png" alt="Analysis view"></td>
<td width="50%"><b>4. Station by station</b><br>A map and per-station split for multi-station datasets.<br><img src="docs/screenshots/04-by-station.png" alt="By station"></td>
</tr>
<tr>
<td width="50%"><b>5. What if we cut it?</b><br>Sliders and presets: deaths avoided and the new smog level.<br><img src="docs/screenshots/05-what-if.png" alt="What-if simulator"></td>
<td width="50%"><b>6. Learn how it works</b><br>A five-step story, each with a "Go deeper" panel.<br><img src="docs/screenshots/06-learn.png" alt="Learn page"></td>
</tr>
<tr>
<td width="50%"><b>7. The research, with wins and losses</b><br>Baselines, shifted-event stress test, literature check, real-data checks, parameter provenance.<br><img src="docs/screenshots/07-evidence.png" alt="Evidence"></td>
<td width="50%"><b>8. Upload preview</b><br>Check your own hourly CSV in the browser. Full attribution still runs in Python.<br><img src="docs/screenshots/08-upload.png" alt="Upload preview"></td>
</tr>
</table>

A **Simple / Detailed** switch inside each dataset hides the technical tables. The page is responsive down to phone width.

<p align="center"><img src="docs/screenshots/09-mobile.png" alt="Mobile layout" width="260"></p>

## How it works
```mermaid
flowchart LR
    A[CPCB hourly PM2.5, PM10,<br>NO2, SO2, CO] --> F
    B[Meteorology:<br>wind, boundary-layer height] --> F
    C[NASA FIRMS fire<br>radiative power] --> F
    D[Station population] --> H
    F[Tracer fingerprinting<br>CO/NO2 traffic, SO2 industry,<br>PM10-PM2.5 dust,<br>FRP x 1/ventilation biomass] --> M
    M[Hierarchical Bayesian<br>receptor model, NUTS] --> I[Identifiability<br>diagnostics]
    M --> H[Health burden<br>GEMM mortality,<br>admissions, counterfactuals]
    M --> V[Falsification<br>synthetic truth, held-out<br>calibration, plume injection]
    V --> K[Interval calibration]
    I --> L[(Ledger + dashboard)]
    H --> L
    K --> L
```

| Step | Code |
|---|---|
| 1. Multi-modal data fusion | `ledger/ingest.py`, `ledger/features.py` |
| 2. Tracer fingerprinting | `ledger/features.py` |
| 3. Hierarchical Bayesian receptor model | `ledger/model.py` (non-negative partially pooled source terms, learned tracer baselines, tracer cross-talk unmixing, proxy-mismatch gain, daily background random walk); `ledger/diagnostics.py` |
| 4. Health-burden propagation | `ledger/health.py` (GEMM mortality, short-term admissions, Monte Carlo over CRF and baseline-rate uncertainty) |
| 5. Falsification and generalisation | `ledger/validate.py`, `ledger/calibration.py` |

## Results
First validation on synthetic episodes (known truth) (12 calibration episodes, 8 held-out):

| Component | Median relative error | 90% interval coverage (raw) | 90% interval coverage (calibrated, held-out) |
|---|---|---|---|
| Road and construction dust | 8% | 63% | 88% |
| Traffic + crop burning (sum) | 8% | 38% | 100% |
| Traffic | 41% | 0% | 100% |
| Crop-residue burning | 20% | 25% | 100% |
| Industry | 55% | 0% | 100% |
| Regional background | 27% | 0% | 75% |

- **Baselines (honest result).** On 8 events with a deliberately shifted source mix, our calibrated ranges contained the truth 80% of the time vs 23% for non-negative least squares; a fixed published split gives no range. Our model is *not* the most accurate point estimate on every source (best on 1 of 5; the fixed split wins when the event resembles the report). Its contribution is calibrated uncertainty and the unresolved-background estimate. See [docs/RESEARCH.md](docs/RESEARCH.md).
- Total PM<sub>2.5</sub> is reproduced inside its 90% predictive band 93% of the time.
- Doubling a source's emissions (plume injection) is detected for both traffic and biomass; for biomass the true value still falls outside the calibrated interval.
- Raw posterior intervals are over-confident. Calibration widens them (x2 to x5) so coverage holds on unseen episodes. This makes the ledger honest, not more precise.
- Traffic and crop burning cannot be separated reliably, so only their sum is reported as reliable.

## Quick start
```bash
pip install -r requirements.txt
python run.py --demo                    # ~10 min: 12 calibration + 8 held-out episodes, plume injection, dashboard
python run.py --demo --skip-validation  # ~30 s: reuse the saved calibration and validation
python run.py --real                    # ~4 min: six real Delhi stations + NASA FIRMS (3 windows); adds them to the dashboard
python -m pytest tests                  # offline tests
```
Open `outputs/dashboard.html`. It is a single file: start on the Home page and pick a dataset card (synthetic demo or real Delhi windows). The Upload page previews your own CSV in the browser; full attribution of uploads is a later feature.

## Real data
The repository ships six real hourly CPCB station files (`data/cpcb/`) and NASA FIRMS daily fire power for Punjab and Haryana, 2018 (`data/firms_viirs_punjab_haryana_daily_2018.csv`). `python run.py --real` fits three windows (before burning, burning peak, after burning) across the six stations and adds them to the dashboard.

| Window | Mean PM<sub>2.5</sub> | Largest source |
|---|---|---|
| Before burning (20 Sep - 4 Oct 2018) | 48 µg/m³ | Regional haze (45%) |
| Burning peak (28 Oct - 11 Nov 2018) | 241 µg/m³ | Regional haze (50%) |
| After burning (26 Nov - 10 Dec 2018) | 201 µg/m³ | Regional haze (50%) |

What the real-data checks show (details in [docs/RESEARCH.md](docs/RESEARCH.md)): the model's 90% predictive band covers 93-94% of observed readings, and it gets the direction of the fire signal right (more burning at the peak). It also compresses the burning swing and gives crop burning about 10% at the peak against about 26% in a published IIT-Kanpur split; we report that gap rather than tune it away.

Your own CPCB-style hourly CSV needs the columns `PM2.5, PM10, NO2, SO2, CO, WS, WD, SR, AT, year, month, day, hour`. The dashboard's Upload page checks a file and previews it in the browser; running the full model on uploads is on the roadmap. Station coordinates in `ledger/realdata.py` are approximate.

## Repository layout
```
run.py                  entry point (demo or real data)
ledger/
  synth.py              synthetic Delhi episodes with known ground truth
  ingest.py             CPCB / Open-Meteo / FIRMS -> model schema
  features.py           tracer fingerprinting
  model.py              hierarchical Bayesian receptor model (NumPyro)
  diagnostics.py        identifiability flags
  health.py             mortality and admissions burden (GEMM verified, ex-China sensitivity)
  baselines.py          NNLS and fixed-published-split baselines, shifted-event stress test
  literature.py         published Delhi apportionment ranges and overlap check
  realdata.py           real CPCB hourly (6 stations) + NASA FIRMS -> model schema
  realcheck.py          out-of-model checks on real data
  synth_alt.py          independent misspecified generator (scoring run pending)
  validate.py           held-out validation and plume injection
  calibration.py        interval calibration
  pipeline.py           end-to-end orchestration
data/cpcb/              six real hourly station files (Jun 2018 - Oct 2019)
data/                   NASA FIRMS daily fire power (Punjab/Haryana, 2018)
dashboard/template.html dashboard source (Home, Datasets, Learn how it works, Upload)
docs/RESEARCH.md        literature, parameter provenance, evidence, what is still to do
outputs/                generated results and dashboard
docs/screenshots/       images used in this README
tests/                  offline tests
```

## Limitations and roadmap
1. **Real data: six stations, one season, no ground truth.** The pipeline runs on six real Delhi stations with NASA fires (`python run.py --real`); it reproduces PM2.5 and gets the burning direction right but compresses the burning swing (see docs/RESEARCH.md). Independent ground truth (speciation campaigns) is still needed.
2. **Partly placeholder health parameters.** GEMM parameters are now verified against the authors' release (see [docs/RESEARCH.md](docs/RESEARCH.md)); Delhi baseline rate, population and the admissions function are still placeholders.
3. **Source separation.** Add explicit source profiles (PMF/CMB-style) and Lagrangian back-trajectories to separate traffic from crop burning.
4. **Unused inputs.** Sentinel-2 land-cover change and OpenStreetMap road and industrial geometries are not yet used.
5. **Live tracking for every station (next).** Stream hourly readings from all stations, refresh the model, and update the source split and health cost live. The current sampler takes minutes per run, so a faster refresh method is part of this work.
6. **Real-data validation.** Leave-one-episode-out on real episodes, the 2020 lockdown as a natural experiment, and triangulation against published apportionment studies.
7. **Upload and new events.** Full attribution on user-uploaded files and a new-event mode.
8. **Sourced health inputs.** Delhi baseline death rate, population weights and an admissions curve.

## License
MIT. See `LICENSE`.
