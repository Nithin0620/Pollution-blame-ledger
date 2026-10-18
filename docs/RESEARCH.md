# Research Foundation

What the literature says, how each design choice follows from it, and what is still unverified. Every figure below was checked against its source; items marked **UNVERIFIED** were not.

## 1. Why source attribution is hard (the gap we target)
| Finding | Source |
|---|---|
| Delhi winter PM2.5 apportionment (IIT Kanpur, chemical mass balance): vehicles 25%, biomass 26%, secondary 30%, solid-waste burning 8%, road/construction dust 6%, coal and fly ash 5%; winter mean about 375 ug/m3 | CSE India, "Restoring Air Quality through Source Apportionment Analysis" (IIT Kanpur data) |
| The same study's emission inventory gives road dust 38% and vehicles 20%: **receptor and inventory methods disagree sharply** | same |
| Inventory estimates range PM2.5 transport 17.9-39.2% and road dust 18.1-37.8% across studies; inventory uncertainty up to 145% | CEEW, "What is Polluting Delhi's Air?" (2019); Kurokawa et al. 2013 |
| Crop-fire activity tracks Delhi PM2.5 (about 50 to about 300 ug/m3 during burning; over 80% of north-westerly flow crossed burning areas) | Jethva et al. 2018, Aerosol & Air Quality Research 18(7) |
| PMF gives no uncertainty on contributions and has rotational ambiguity, so non-uniqueness is not reported | Park & Oh 2015, Chemometrics & Intelligent Lab. Systems 149:215-226 |

**Gap:** published splits disagree, carry no calibrated uncertainty, and never state which sources the data cannot separate. Our contribution is to report all three.

## 2. Method choices and their grounding
| Our component | Why | Grounding |
|---|---|---|
| Hierarchical Bayesian receptor model (NUTS) with tracer proxies | Gives full posteriors instead of point splits; partial pooling across stations | Receptor-modelling family (CMB / PMF); Bayesian treatment addresses Park & Oh's uncertainty criticism |
| Identifiability diagnostics (posterior correlation, information gain) | Collinear tracers make some pairs inseparable; we flag and report their sum | Addresses PMF rotational ambiguity |
| Split-conformal calibration of intervals | Raw posteriors were over-confident (coverage 0-63%); calibration restores finite-sample marginal coverage | Lei et al. 2018 (JASA), arXiv 1604.04173 |
| Plume injection with known truth | Receptor results rarely have ground truth, so we falsify by injecting a known change | Standard synthetic-benchmark practice |
| GEMM mortality, counterfactual source removal | Covers the full PM2.5 range seen in Delhi, unlike linear or log-linear functions | Burnett et al. 2018, PNAS 115(38) |

## 3. Health parameters: verified vs. still placeholder
**Verified against the authors' data release** (GEMM Calculator workbook, sheet "GEMM fit parameters"; github.com/mszyszkowicz/DataGEMM), NCD+LRI, ages 25+, all regions:
theta 0.1430 (SE 0.01807), alpha 1.6, mu 15.5, nu 36.8, counterfactual 2.4 ug/m3. These match `ledger/health.py` exactly.

**Sensitivity:** the authors also publish a fit excluding China (theta 0.1231, alpha 1.5, mu 10.4, nu 25.9). At 300 ug/m3 it gives an attributable fraction of 0.479 vs 0.527 (about 9% lower); at 60 ug/m3 the two agree (0.322 vs 0.324). The headline is therefore insensitive to this choice at moderate levels and modestly sensitive at Delhi-winter levels. Age-specific parameters (25-29 ... 80+) are also available and are the planned upgrade.

**Short-term context:** Lancet Planetary Health 2024 (10 Indian cities) reports +1.4% daily mortality per 10 ug/m3 pooled, **+0.31% for Delhi**, and 7.2% of daily deaths above the WHO guideline. We use GEMM (long-term), not this, for the burden; it is a useful cross-check on order of magnitude. Confidence intervals were not retrieved.

**Still placeholder (be upfront about these):**
- Baseline NCD+LRI mortality rate 0.0028 per adult-year. The GEMM workbook holds India age-specific 2015 GBD death counts but no Delhi rate. Delhi's Births & Deaths Report 2021 gives 171,476 registered deaths (8.28 per 1,000, place of occurrence, COVID year), which is not a clean resident rate.
- Delhi population and adult share. **UNVERIFIED.**
- Hospital-admissions function (RR 1.008 per 10 ug/m3). The Delhi mortality figure above is a different outcome and must not be substituted.

## 4. Evidence implemented in the code (synthetic data, known truth)
**Baselines** (`ledger/baselines.py`, same data and same truth). Median relative error per source, 8 new events whose source mix was deliberately shifted (each source scaled 0.4x to 2.5x):

| Source | Our model | NNLS | Fixed published split |
|---|---|---|---|
| Vehicles | 53% | 27% | **22%** |
| Factories | 125% | 348% | **32%** |
| Road dust | 35% | **19%** | 68% |
| Crop burning | 22% | 24% | **19%** |
| Regional haze | **29%** | 100% | 49% |
| Ranges containing the truth (target 90%) | **80%** | 23% | none given |

Reading: we do **not** win on point accuracy for most sources. The static split is competitive and cannot adapt (it fails badly on road dust); plain least squares is overconfident (23% coverage). The contribution is calibrated uncertainty plus honest separation limits, not a lower point error. On familiar, report-like events the fixed split is best on 3 of 5 sources, which is expected because the synthetic generator is built around Delhi's published profile.

**Literature benchmark** (`ledger/literature.py`): every run compares each source's 90% share range with the IIT Kanpur and CEEW figures. On the demo episode vehicles, crop burning and road dust overlap a published figure; factories do not (13% vs 5% for coal/fly ash, a loose category match). Agreement on synthetic data is by construction and is not validation; the check is built for a real episode.

**Health sensitivity**: the authors' ex-China GEMM fit lowers total attributable deaths from 791 to 723 (about 9%), inside our uncertainty range.

## 5. Real-data evidence (six Delhi CPCB/DPCC stations + NASA FIRMS, autumn 2018)
Run with `python run.py --real` (about 4 minutes). Data in `data/` (hourly CPCB files for Ashok Vihar, Dwarka Sec-8, Najafgarh, Okhla, Nehru Nagar and Major Dhyan Chand Stadium supplied by the team; FIRMS VIIRS S-NPP country archive filtered to Punjab/Haryana, daily FRP). Three 14-day windows: before burning (20 Sep), burning peak (28 Oct), after burning (26 Nov).

| Check | Result |
|---|---|
| Observed PM2.5 reproduced inside the 90% predictive band | 93% / 94% / 93% of hours |
| Convergence | R-hat <= 1.04, no divergences (the sampler now re-seeds automatically when chains disagree) |
| Crop burning higher in the peak than before / after (posterior probability) | 1.00 / 1.00 |
| Satellite fire power, peak vs after | about 78x |
| Our crop-burning estimate, peak vs after | 24.5 vs 14.7 ug/m3, about 1.7x (**the swing is compressed**) |
| Peak-window burning share vs IIT Kanpur winter 26% | 10% (5-15%): **does not overlap** |

Honest reading: the model reproduces real PM2.5 at six stations and gets the direction of the burning signal right, but under-states the size of the swing and the burning share against the literature. Likely causes (not tested): winter heating smoke leaking into the burning term, a fixed 5-18 h transport lag, a regional rather than wind-traced fire footprint, and a boundary-layer proxy. Limits: stations share one airshed meteorology (cross-station median), boundary-layer height is a solar-radiation proxy, the CPCB files look gap-filled by interpolation, station coordinates are approximate and population weights are an equal-split placeholder, and there is no source-level ground truth.

## 6. Still to do
1. The Mar-Apr 2020 lockdown natural experiment (needs those CPCB files) and the 2019 season (the supplied files end 1 Oct 2019).
2. Wind-traced fire footprint (back-trajectories) and ERA5 boundary-layer height.
3. Age-specific GEMM, a sourced Delhi baseline rate, population and admissions function.
4. NMF/PMF baseline (we used NNLS and a fixed split).
5. Out-of-model stress test (`ledger/synth_alt.py`: a generator with different structure from the model) is written but its scoring run is not yet done.

## References
- Burnett R. et al. (2018). Global estimates of mortality associated with long-term exposure to outdoor fine particulate matter. PNAS 115(38). https://www.pnas.org/doi/10.1073/pnas.1803222115
- CEEW (2019). What is Polluting Delhi's Air? https://www.ceew.in/publications/delhi-air-pollution-sources-and-causes
- CSE India. Restoring Air Quality through Source Apportionment Analysis. https://cdn.cseindia.org/attachments/0.12136100_1560416301_Restoring-Air-Quality-through-Source-Apportionment-Analysis.pdf
- Jethva H. et al. (2018). Aerosol and Air Quality Research 18(7).
- Lei J. et al. (2018). Distribution-free predictive inference for regression. JASA. arXiv:1604.04173
- Park S.S., Oh (2015). Chemometrics and Intelligent Laboratory Systems 149:215-226.
- Lancet Planetary Health (2024). Short-term PM2.5 and mortality in 10 Indian cities. https://thesouthfirst.com/health/over-7-of-daily-deaths-in-10-indian-cities-linked-to-pm2-5-pollution-lancet-study/
- Delhi Directorate of Economics & Statistics. Annual Report on Registration of Births & Deaths 2021.
