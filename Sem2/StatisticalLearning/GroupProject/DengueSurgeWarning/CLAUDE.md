# Context for Claude Code - Dengue Surge Warning

Project brief: Ref 1.1 "Dengue surge warning", public health, intermediate level.
Required tools: logistic regression, regression, model selection, trees.
Report and proposal in English (LaTeX). User chats in Vietnamese - reply in Vietnamese.

## Decisions already made (with the user)
- Surge target: try BOTH definitions and compare
  - A threshold: y[t+h] > mean + k*sd of previous 52 weeks (k=1.5)
  - B growth: y[t+h] >= (1+pct)*y[t] and y[t+h] >= min_cases (pct=0.25, min=50)
  - horizons h = 1, 2, 4 weeks
- Spatial scope: start national weekly, extend to regional/cluster level later if time allows.
- Main case data: MOH Weekly Infectious Disease Bulletin, data.gov.sg id d_ca168b2cb763640d72c4600a68f9909e (2012-2022).
  The original link (d_dbfabf16158d1b0e1c420627c0819168, NEA dengue clusters) is only a current snapshot, not a time series.
- Weather: Open-Meteo archive API (daily -> weekly, ISO weeks aligned with MOH epi weeks).
- Validation: rolling-origin CV by year from 2017, purge h weeks; main metric PR-AUC.

## Status (2026-10-15)
- Iterations 0-3 done on REAL data (venv: pipeline/.venv). Summary + figures in visualize/ (README there).
- Fixed: MOH epi weeks use the MMWR Sun-Sat calendar, not ISO (2014 has W53, not 2015).
- Tuned: k=2.0; growth pct per horizon {1:0.25, 2:0.30, 4:0.45} -> prevalence 12-20%.
- Redesigned to match the lecturer's brief (1.1): DF target (DHF separate), targets thr / seas (p90 same
  season) / grow + onset variants, baselines prior / seasonal / persistence, rolling origin by week
  (refit_every=4), cost-based alarm threshold, calibration, block bootstrap, reporting-delay sensitivity.
- Findings: A and S dominated by persistence; S-onset is where count models add value (few positives);
  B hard. Details in visualize/README.md. One-page proposal: proposal/proposal.tex (compile with tectonic).
- Still to do: main analysis on MOH 2014-2018 + NEA weather (brief's sources); final run refit_every=1.

## Known caveats / open items
- Case data on the API ends 2022; 2023+ would need NEA/CDA bulletins or OpenDengue.
- `prior` baseline pooled ROC-AUC is not meaningful (constant per fold).
- statsmodels is in requirements but unused so far (planned: negative binomial GLM).
- Verify the 3 entries in report/references.bib before submission.
- Workflow: see pipeline/README.md (iteration table). Dataset links: potential_datasets/potential_datasets.md.
