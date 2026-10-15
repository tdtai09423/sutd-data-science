from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_config(path=None):
    path = Path(path) if path else ROOT / "config.yaml"
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    for k, v in cfg["paths"].items():
        p = ROOT / v
        p.mkdir(parents=True, exist_ok=True)
        cfg["paths"][k] = p
    (cfg["paths"]["outputs"] / "figures").mkdir(exist_ok=True)
    (cfg["paths"]["outputs"] / "tables").mkdir(exist_ok=True)
    return cfg


def write_summary(cfg, name, lines):
    """Every stage writes outputs/<name>_summary.md - this is what you send back for review."""
    path = cfg["paths"]["outputs"] / f"{name}_summary.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n[summary] {path}")
    return path
