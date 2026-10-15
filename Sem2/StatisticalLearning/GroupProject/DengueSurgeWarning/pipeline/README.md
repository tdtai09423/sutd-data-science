# Pipeline

## Setup
```bash
cd pipeline
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# optional, for higher data.gov.sg rate limits:
export DATAGOV_API_KEY=...         # Windows: set DATAGOV_API_KEY=...
```

## Stages
```bash
python run.py fetch      # download raw data -> data/raw/
python run.py inspect    # describe raw files
python run.py build      # weekly cases + weather -> data/processed/weekly.csv
python run.py eda        # plots + lagged correlations
python run.py features   # predictors + surge targets -> data/processed/model_table.csv
python run.py model      # rolling-origin CV comparison of models
python run.py all        # everything
```
Every stage writes `outputs/<stage>_summary.md`. Figures go to `outputs/figures/`,
tables to `outputs/tables/`. Settings (lags, horizons, surge thresholds, test years)
are in `config.yaml` - change them there, not in code.

## Iterative workflow (dev loop)
Each iteration: run a stage -> send back its `*_summary.md` (+ figures) -> decide the next change.

| Iter | Run | Send back | Decision it informs |
|------|-----|-----------|---------------------|
| 0 | fetch, inspect | fetch_summary.md, inspect_summary.md | do column names / disease names parse correctly? |
| 1 | build, eda | build_summary.md, eda_summary.md, eda_*.png | missing weeks, epidemic years, which weather lags matter |
| 2 | features | features_summary.md, features_targets.png | tune surge thresholds (k, pct) so prevalence is ~10-20% |
| 3 | model | model_summary.md, feature_importance.csv, tree_rules.txt | which target/horizon/model to focus on |
| 4+ | edits from results | same | tuning, feature selection, robustness, spatial extension |

## Design notes
- Target series: weekly dengue fever (DF). DHF is kept separate (under 1 case/week on average).
- Surge definitions (fixed before fitting; all thresholds known at forecast week t):
  - A `thr`: y[t+h] > mean + k*sd of the previous 52 weeks.
  - S `seas`: y[t+h] > q-th percentile of the same season (+-17 days) in earlier years.
  - B `grow`: y[t+h] >= (1+pct[h])*y[t] and y[t+h] >= min_cases.
  - `thronset` / `seasonset`: A / S restricted to weeks where y[t] is not yet above the threshold
    (genuine early warning; few positives).
- Validation: rolling origin by week with an expanding window from `first_test_year`; models are
  refitted every `refit_every` weeks and training rows are purged so every label is known at the origin.
- Baselines: prior, seasonal (historical surge rate for the week of year), persistence
  (logistic on the current distance to the threshold, or on last week's growth for B).
- Count regressions (Poisson GLM, ridge on log counts) are turned into P(surge) with a log-normal
  predictive distribution, so every model is scored on PR-AUC, Brier and calibration.
- Alarm when P >= 1/(1+cost_ratio); `alarm_cost_tradeoff.csv` shows other cost ratios.
- 95% CIs by moving-block bootstrap (26-week blocks) of the out-of-sample predictions.
- Reporting-delay sensitivity: h=1 targets re-run with week t's counts treated as unknown.
- MOH epi weeks (Sun-Sat, MMWR numbering) are keyed by the following Monday; weather uses Mon-Sun weeks.
