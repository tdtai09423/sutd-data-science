# Dengue Surge Warning (Singapore)

**Project Ref 1.1 | Statistical Learning | Public health**

Can recent dengue counts and weather conditions help identify weeks with an elevated risk of a
dengue surge in Singapore? This project compares surveillance-only, weather-only and combined
forecasts at 1-, 2- and 4-week horizons. It is a predictive study, not a causal analysis or a
clinical/public-health alert system.

## Project contents

| path | contents |
|---|---|
| `pipeline/` | Reproducible data retrieval, cleaning, EDA, feature construction and rolling-origin evaluation |
| `pipeline/config.yaml` | Main analysis: MOH bulletin and NEA/MSS Changi weather, 2012-2022; final 2022 holdout |
| `pipeline/config_brief.yaml` | Secondary analysis on the brief's MOH 2014-2018 case series |
| `pipeline/data/processed/` | Committed analysis-ready weekly case and weather snapshots |
| `docs/DATA.md` | Data sources, provenance, data dictionary, QA and limitations |
| `report/` | LaTeX report source, references and figures |
| `proposal/` | One-page proposal source and PDF |
| `visualize/` | Summary plots and Vietnamese guide |
| `AI_USE.md` | AI-use disclosure |
| `potential_datasets/` | Dataset links and source notes |

Course requirement PDFs and converted text under `Requirement/` are intentionally gitignored;
they are instructor materials and must not be published in this public repository.

## Reproduce the analysis

Requires Python 3.9+ and the packages in `pipeline/requirements.txt`.

```bash
cd pipeline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py all
```

`run.py all` fetches public source data, builds weekly data, runs EDA and features, then evaluates
the models. Raw downloads are intentionally not committed; the fetch stage records provenance and
checksums in `data/raw/MANIFEST.json`. The processed weekly snapshots are committed so the data
preparation and analysis can also be inspected without downloading the raw files.

Run the shorter, brief-source analysis separately:

```bash
cd pipeline
.venv/bin/python run.py all --config config_brief.yaml
```

The secondary analysis is a feasibility / cross-check analysis, not a replacement for the main
analysis: the five-year series has too few surge positives in its later test years for stable
evaluation.

## Analysis design

* **Outcome:** weekly national dengue fever (DF) counts. Dengue haemorrhagic fever (DHF) is kept
  separate because it is rare.
* **Predictors:** lagged case counts and weather; weather includes MSS Changi rainfall/temperature
  and Open-Meteo humidity.
* **Targets:** rolling threshold exceedance, historical same-season 90th percentile, growth, and
  onset-only variants; horizons are 1, 2 and 4 weeks.
* **Models:** seasonal and persistence baselines; logistic regression (case, weather and combined),
  lasso logistic regression, CART, random forest, Poisson GLM and ridge regression on log counts.
* **Validation:** expanding-window rolling-origin by week beginning in 2016, with target weeks
  before 2022 used for development and target weeks in 2022 reported separately. Training rows
  are purged by forecast horizon; tuning is forward-chained; uncertainty uses moving-block
  bootstrap. Earlier 2022 labels can enter later rolling training windows, and earlier exploratory
  runs included 2022, so the final period is not a pristine static holdout.
* **Metrics:** PR-AUC, precision, recall, Brier score/calibration and regression MAE/RMSE. The
  project does not use accuracy as its primary metric.

Details, target formulas, dataset licences, sources and checks are in [`docs/DATA.md`](docs/DATA.md)
and [`pipeline/README.md`](pipeline/README.md). The machine-readable configuration is
[`pipeline/config.yaml`](pipeline/config.yaml).

## Build the report and visuals

```bash
cd report && tectonic main.tex
cd ../proposal && tectonic proposal.tex
cd ..
pipeline/.venv/bin/python visualize/make_visuals.py
```

The pipeline writes summaries to `pipeline/outputs/` and tables/figures to its `tables/` and
`figures/` subdirectories. Summary charts are generated in `visualize/figures/`.
