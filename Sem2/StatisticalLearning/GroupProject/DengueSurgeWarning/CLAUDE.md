# Context for Claude Code - Dengue Surge Warning

Project brief: Ref 1.1 "Can next week's dengue surge be flagged early?", public health, intermediate level.
Required tools: logistic regression with lagged variables, regularisation, regression for (transformed)
counts, CART/random forest, seasonal and persistence baselines. Validation: rolling origin by week,
recall / precision / PR-AUC / calibration. Defence: reporting revisions, immunity/serotypes, few outbreaks,
cost of false alarms. Brief's sources: MOH weekly DF + DHF 2014-2018 and NEA weather (data.gov.sg).
Report and proposal in English (LaTeX). User chats in Vietnamese - reply in Vietnamese.

## Working preferences (from the user)
- Commits are authored by the user only: never add Co-Authored-By / Claude attribution lines.
- Pushing straight to `main` is fine. The git root is the whole master's folder
  (repo tdtai09423/sutd-data-science, PUBLIC): stage only this project folder unless asked.

## Current design (all settings in pipeline/config.yaml)
- Case data: MOH Weekly Infectious Disease Bulletin, data.gov.sg d_ca168b2cb763640d72c4600a68f9909e
  (2012-2022). Target series = dengue fever (DF); DHF kept separate (too rare).
  MOH epi weeks use the MMWR Sun-Sat calendar (2014 has W53), keyed by the following Monday.
- Weather: Open-Meteo archive (daily -> Mon-Sun weeks), lags 0-12 weeks.
- Targets, h = 1 (primary), 2, 4:
  - thr: y[t+h] > mean + 2.0*sd of past 52 weeks
  - seas: y[t+h] > p90 of same season (+-17 days) in earlier years (only weeks > 26 wk before t+h)
  - grow: y[t+h] >= (1+pct[h])*y[t] and >= 50, pct = {1: 0.25, 2: 0.30, 4: 0.45}
  - thronset / seasonset: thr / seas only where y[t] is not yet above the threshold
- Models: prior, seasonal, persistence baselines; logit (cases / weather / full); lasso logit
  (C by forward-chaining CV); CART depth 3; random forest; Poisson GLM; ridge on log counts.
  Count models -> P(surge) via log-normal predictive distribution.
- Evaluation: rolling origin by week from 2017, expanding window, refit_every = 4, purge h weeks;
  alarm if P >= 1/(1+cost_ratio), cost_ratio = 4; 95% moving-block bootstrap (26 wk);
  1-week reporting-delay sensitivity for h = 1.

## Status (2026-10-16)
- Pipeline runs end to end on real data (venv: pipeline/.venv, Python 3.9). Summary + figures in
  visualize/ (README in Vietnamese). One-page proposal: proposal/proposal.tex (compile with tectonic).
- Findings: thr and seas are dominated by persistence (PR-AUC ~0.96); seasonset is where count models
  add value (PR-AUC 0.94 vs 0.51, but only 7 test positives); grow is hard (~0.26-0.33);
  weather alone adds little; simple models >= RF/CART.

## Next steps
1. Main analysis on the brief's sources: MOH DF/DHF 2014-2018 (d_ac1eecf0886ff0bceefbc51556247015,
   already fetched) + NEA weather (historical daily records d_03bb2eb67ad645d0188342fa74ad7066 cover
   2009 - Nov 2017; check coverage, else Open-Meteo cross-checked with NEA monthly series).
   Keep 2012-2022 as the robustness analysis. 2014-2018 needs an earlier first_test_year.
2. Final run with refit_every = 1 (~30 min).
3. Rewrite report/sections/*.tex: they are still the old skeleton (two targets, by-year CV, gradient boosting).
4. Verify the entries in report/references.bib.
- Group: Tran Duy Tai, Do Nhat Thanh, Nguyen Thi Quynh Thu.
- The proposal (revised 2026-10-17) drops CART / random forest and the cost-ratio alarm threshold;
  the pipeline and visualize/ still include them.

## Known caveats
- Case data on the API ends 2022; 2023+ would need NEA/CDA bulletins or OpenDengue.
- statsmodels is in requirements but unused (negative binomial GLM is optional).
- Workflow: pipeline/README.md. Dataset links: potential_datasets/potential_datasets.md.
