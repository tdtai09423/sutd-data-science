"""Entry point.  python run.py <stage> [--force]

Stages (run in order the first time):
  fetch     download raw data            -> data/raw/,       outputs/fetch_summary.md
  inspect   describe raw files            -> outputs/inspect_summary.md
  build     weekly cases + weather table  -> data/processed/weekly.csv
  eda       plots, lagged correlations    -> outputs/figures/eda_*.png, outputs/eda_summary.md
  features  predictors + surge targets    -> data/processed/model_table.csv
  model     CV model comparison           -> outputs/tables/*.csv, outputs/model_summary.md
  all       everything above
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from dengue import build, eda, features, fetch, inspect_data, modeling  # noqa: E402
from dengue.config import load_config  # noqa: E402

STAGES = ["fetch", "inspect", "build", "eda", "features", "model"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=STAGES + ["all"])
    ap.add_argument("--force", action="store_true", help="re-download even if raw files exist")
    ap.add_argument("--config", default=None)
    a = ap.parse_args()
    cfg = load_config(a.config)
    todo = STAGES if a.stage == "all" else [a.stage]
    for s in todo:
        print(f"\n######## {s} ########")
        if s == "fetch":
            fetch.run(cfg, force=a.force)
        elif s == "inspect":
            inspect_data.run(cfg)
        elif s == "build":
            build.run(cfg)
        elif s == "eda":
            eda.run(cfg)
        elif s == "features":
            features.run(cfg)
        elif s == "model":
            modeling.run(cfg)


if __name__ == "__main__":
    main()
