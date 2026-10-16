# Dengue Surge Warning (Singapore)

Ref 1.1 | Public health | Intermediate | Logistic regression, regression, model selection, trees

```
DengueSurgeWarning/
├── pipeline/             Python pipeline (data -> features -> models)
├── report/               LaTeX report (main.tex, sections/, references.bib)
├── proposal/             LaTeX proposal (proposal.tex, uses ../report/references.bib)
└── potential_datasets/   potential_datasets.md - plain-text list of data links
```

Quick start: see `pipeline/README.md`.
Build LaTeX: `cd proposal && tectonic proposal.tex` (same for `report/main.tex`; `latexmk -pdf` also works).
Summary figures: `pipeline/.venv/bin/python visualize/make_visuals.py` -> `visualize/`.
The report reads figures straight from `pipeline/outputs/figures/`.
