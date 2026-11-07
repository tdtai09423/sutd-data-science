# Project context: Dengue Surge Warning (Singapore)

Project Ref 1.1, 42.510 Statistical Learning. Main question: can recent dengue counts and
weather conditions help identify weeks with elevated surge risk in Singapore? This is a
retrospective predictive study, not causal inference or a live alert.

## Deliverables and language

- User chats are in Vietnamese; reply in Vietnamese.
- Proposal, report and slides are in English and LaTeX.
- Follow `README.md`, `docs/DATA.md` and the rubric-derived requirements in the ignored
  `Requirement/` folder.
- The final report is limited to 6 A4 pages of main text (11-12 pt), excluding references and a
  concise appendix. Required topics include question/relevance, curation, methods/validation,
  results, discussion/ethics, reproducibility/contributions, references and AI disclosure.

## Current analysis design

The primary configuration is `pipeline/config.yaml`:

- Cases: MOH Weekly Infectious Disease Bulletin, data.gov.sg dataset
  `d_ca168b2cb763640d72c4600a68f9909e`, 2012-2022. Dengue fever (DF) is the target series;
  dengue haemorrhagic fever (DHF) is retained separately because it is rare.
- Cross-check / secondary analysis: MOH DF/DHF 2014-2018,
  `d_ac1eecf0886ff0bceefbc51556247015`, also in `pipeline/config_brief.yaml`.
- Weather: NEA/MSS daily Changi station S24 rainfall and temperature (2011-06 to 2022-12);
  Open-Meteo humidity, checked against NEA monthly Changi humidity.
- MOH epi weeks use MMWR Sunday-Saturday numbering and are keyed by the following Monday to
  align them with Monday-Sunday weather weeks. 2014 and 2020 have 53 weeks.
- Outcomes at horizons h = 1, 2, 4:
  - `thr`: y[t+h] > mean + 2 SD of the past 52 weeks.
  - `seas`: y[t+h] > p90 for the same season (+/-17 days) in earlier years, excluding the most
    recent 26 weeks.
  - `grow`: y[t+h] >= (1 + pct[h]) y[t] and >= 50, pct = 0.25, 0.30, 0.45.
  - `thronset` / `seasonset`: threshold / seasonal targets only when y[t] is not already above
    the relevant threshold.
- Models: prior, seasonal and persistence baselines; logistic regression (cases/weather/full);
  lasso logistic regression; depth-3 CART; random forest; Poisson GLM; ridge on log counts.
  Count forecasts are converted to probabilities of crossing the target threshold.
- Validation: expanding-window rolling origin by week from 2016, refit every week, purge labels
  by horizon. Development is defined by target weeks before 2022; target weeks in 2022 are
  reported separately. Earlier observed 2022 labels may enter training for later rolling
  forecasts. Report PR-AUC,
  precision, recall, Brier/calibration, alarms per year and count-regression MAE/RMSE; use
  26-week moving-block bootstrap intervals.
- The primary alarm threshold corresponds to missed-surge:false-alarm cost ratio 4:1; report
  the sensitivity across the configured cost-ratio grid.

## Caveats to state, not hide

- The 2014-2018-only analysis has too few late-period surge events for stable evaluation; it is
  a source cross-check and secondary feasibility analysis.
- Exploratory runs before the final holdout design pooled forecasts through 2022. Thus 2022 was
  seen during development; the final rolling evaluation also incorporates earlier 2022 outcomes
  in later training windows. Describe it as a final-period prequential check, not an independent
  pristine static test.
- MOH data on data.gov.sg end in 2022. Later coverage needs another source.
- Only national aggregate cases and one weather station are available; immunity, serotypes,
  spatial exposure and reporting changes are not modelled.
- Rainfall and humidity cross-check less well than temperature; discuss these measurement limits.
- A favorable result for onset targets may be based on very few positive events and wide
  uncertainty intervals.

## Status (2026-11-07)

- Final main run done (refit weekly, ~9 h); `run.py evaluate` re-scores saved OOF predictions.
- Report (report/main.pdf, 5 pages + refs + appendix) and slides (slides/slides.pdf, 13 frames) are
  filled with final numbers. Open items: contributions split (red placeholder in report section 7
  and the slides appendix), rehearsal, and checking that every member presents.
- Key result: persistence ≈ best for level surges (PR-AUC 0.93-0.97); count models help growth
  (0.26 vs 0.17) and S-onset (0.89 vs 0.26, 5 events); weather adds nothing.

## Reproducibility

Run the main pipeline with `cd pipeline && .venv/bin/python run.py all`; the brief-source run is
`.venv/bin/python run.py all --config config_brief.yaml`. Raw downloads are ignored; provenance
is in `pipeline/data/raw/MANIFEST.json`. The processed weekly files are committed. Regenerate
summary figures with `pipeline/.venv/bin/python visualize/make_visuals.py`.

The git root is the master's folder. Stage only `Sem2/StatisticalLearning/GroupProject/DengueSurgeWarning/`
unless asked otherwise. The user authors commits; do not add co-author attribution lines.
