# Analysis pipeline

The pipeline retrieves source data, creates weekly analysis tables and evaluates the forecasting
models. The main configuration is `config.yaml`; `config_brief.yaml` runs the brief's 2014-2018
case series as a secondary analysis.

## Setup

```bash
cd pipeline
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Optional: higher data.gov.sg rate limits
export DATAGOV_API_KEY=...          # Windows: set DATAGOV_API_KEY=...
```

## Run

```bash
python run.py fetch      # public raw sources -> data/raw/ and provenance manifest
python run.py inspect    # inspect downloaded raw files
python run.py build      # MOH cases + weekly weather -> data/processed/
python run.py eda        # exploratory summaries and plots
python run.py features   # lagged predictors and surge targets
python run.py model      # rolling-origin model evaluation
python run.py all        # run every stage
python run.py evaluate   # re-score saved out-of-sample predictions (no refits)
```

With `refit_every: 1` the `model` stage takes about 9 hours (every model is refitted every week for
every target). `evaluate` reads `data/processed/oof_predictions.csv` and rebuilds all tables,
figures and the summary in about 10 minutes (most of it is the reporting-delay sensitivity).

The brief-source sensitivity analysis is:

```bash
python run.py all --config config_brief.yaml
```

Every stage writes `outputs/<stage>_summary.md`. Tables are in `outputs/tables/`, and plots are
in `outputs/figures/`. Configuration values (sources, lags, horizons, thresholds, test periods,
bootstrap settings) should be changed in the YAML files, not hard-coded in Python.

## Data and provenance

The main series is MOH weekly dengue fever (DF), 2012-2022. DHF remains separate because it is
rare. Weekly rainfall and temperature use NEA/MSS Changi station S24; weekly relative humidity
uses Open-Meteo and is checked against NEA monthly Changi humidity. The data.gov.sg Admiralty
daily weather series does not cover the full study period.

`fetch` writes `data/raw/MANIFEST.json` with source metadata, retrieval dates, URLs, licences and
SHA-256 hashes. Raw downloads are not committed. The processed weekly snapshots are tracked to
support reproducibility and inspection. Consult [`../docs/DATA.md`](../docs/DATA.md) for the full
data dictionary, inclusion criteria, QA results, joins and limitations.

## Design and evaluation

* **Targets:** (A) next-period cases above the past-52-week mean + 2 SD; (S) above the historical
  same-season 90th percentile; (B) growth by a horizon-specific percentage and at least 50 cases.
  A-onset and S-onset restrict A/S to weeks not already over the threshold. Horizons: 1, 2 and 4
  weeks.
* **Predictors:** current and lagged log cases, rolling case summaries, growth, seasonal terms,
  and weather lags from 0 to 12 weeks. Only information available by the forecast origin is used.
* **Models:** prior, seasonal and persistence baselines; logistic regression on cases/weather/full
  features; lasso logistic regression; depth-3 CART; random forest; Poisson GLM; and ridge on
  log-counts. Count forecasts are mapped to surge probabilities.
* **Validation:** expanding-window rolling-origin by week from 2016, refitting every week.
  Training examples are purged so their full outcome horizon is known at forecast time. Target
  weeks before 2022 are development; target weeks in 2022 are reported separately. Lasso tuning
  uses forward-chaining CV within the training window. Earlier observed 2022 outcomes can enter
  training for later rolling forecasts, but holdout metrics must not guide model selection.
  Earlier exploratory runs included forecasts through 2022, so this is not a pristine static
  holdout.
* **Metrics:** PR-AUC and its 95% moving-block-bootstrap interval (26-week blocks), precision,
  recall, alarms per year and Brier/calibration; count models also report MAE and RMSE.
* **Sensitivity:** a one-week reporting-delay case-count assumption is evaluated for the primary
  one-week targets.

The baseline alarm threshold uses the specified relative cost assumption; the cost trade-off table
shows other ratios. The analysis is a retrospective forecasting exercise, not a deployed alert.

## Outputs and iteration

For model results inspect `outputs/model_summary.md`, `outputs/tables/model_cv_pooled.csv`,
`model_cv_by_year.csv`, `feature_importance.csv`, `tree_rules.txt` and
`delay_sensitivity.csv`. Use the development period for model selection and report the holdout
once, separately. Regenerate the summary figures from the project root:

```bash
pipeline/.venv/bin/python visualize/make_visuals.py
```
