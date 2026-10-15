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
- Surge A (threshold): y[t+h] > mean + k*sd of the previous 52 weeks.
- Surge B (growth): y[t+h] >= (1+pct)*y[t] and y[t+h] >= min_cases.
- All predictors use information up to week t only; CV trains on all weeks before each
  test year and drops the last h training weeks (no target overlap).
- Count regressions (Poisson GLM, Poisson GBM) are turned into alarms with the same rule
  as the target, so classification and regression are compared on equal terms.
- MOH epi weeks (Sun-Sat) are mapped to ISO weeks (Mon-Sun), a 1-day shift, applied
  identically to weather.
- `prior` model is a reference for PR-AUC / Brier only (its pooled ROC-AUC is not meaningful).
