# AI-use disclosure

Required by the project rules (42.510, Project Rules and Rubric).
The group remains responsible for every claim, number and line of code in this package.

## Tools

| tool | used for | period |
|---|---|---|
| AI coding assistant (Copilot SDK agent in VS Code; earlier sessions with Claude Code) | code for the data pipeline, debugging data-format problems, drafting documentation, LaTeX report and slides | Oct - Nov 2026 |

## What it was used for

1. **Data retrieval and cleaning code** (`pipeline/src/dengue/fetch.py`, `build.py`):
   * data.gov.sg API and MSS download code;
   * the provenance manifest;
   * parsing of the MOH epi-week calendar;
   * fixes for mixed file encodings (latin-1 and UTF-8 with a BOM) in the MSS daily files.
2. **Modelling code** (`features.py`, `modeling.py`):
   * rolling-origin evaluation with purging;
   * moving-block bootstrap;
   * conversion of count-model forecasts into surge probabilities;
   * the split between the development period and the final test period.
3. **Figures** (`visualize/make_visuals.py`, `pipeline/src/dengue/eda.py`).
4. **Writing support**:
   * first drafts of `docs/DATA.md`, the READMEs, report sections and slides;
   * conversion of the course PDFs to text so their requirements could be checked.

## Representative prompts (translated from Vietnamese where needed)

* "Read the project and tell me what is implemented; describe the topic and its purpose."
* "Complete the project using Singapore data and research; tell me what is still missing to
  implement the whole project end to end."
* "Implement PDF-reading skills so you can read the requirement documents, and adjust the
  project to the rubric criteria."
* Decisions put to the group by the assistant and answered by us:
  * use 2012-2022 as the main analysis, with the brief's 2014-2018 file as cross-check and
    secondary analysis;
  * hold out 2022 as the final test year.

## What was AI-generated

* Most of the Python code in `pipeline/` and `visualize/`.
* First drafts of the documentation, report text and slides.

## What was decided or written by the group

* The research question.
* The surge definitions and their parameters.
* The choice of models and the validation design.
* The interpretation of results and the final wording of the report.

## How outputs were checked

* **Data**:
  * Totals were compared across two MOH releases (209 of 261 weeks identical, maximum
    difference 8 cases).
  * Weather was cross-checked between MSS, Open-Meteo and NEA monthly humidity.
  * Duplicate, missing-week and range checks were run.
  * All checks are in `pipeline/outputs/build_summary.md`.
* **Leakage**:
  * Every predictor is lagged to week *t*.
  * Training rows whose label lies after the forecast origin are purged.
  * Thresholds use only past data.
  * Tuning (lasso C) uses forward-chaining CV inside the training window.
  * Scores for target weeks in 2022 are reported separately and do not guide model
    selection. In the rolling evaluation, earlier 2022 labels can enter training for
    later forecasts after those outcomes become observable.
* **Results**:
  * Every number in the report is read from files written by the pipeline
    (`pipeline/outputs/*.md`, `outputs/tables/*.csv`).
  * Re-running `python run.py all` reproduces them, with fixed random seeds.
* **Citations**: each reference was checked against the publisher page or DOI. The AI tool was
  not trusted to supply references.

## Known limitation of AI use

Exploratory runs before the final design pooled forecasts through 2022, so that period was seen
during development. The final evaluation also uses a rolling update as earlier 2022 outcomes
become available. It is not an untouched static holdout; the report states these qualifications.
