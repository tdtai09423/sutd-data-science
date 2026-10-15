"""Stage `inspect`: describe every raw file so we can decide how to build the dataset."""
import json

import pandas as pd

from .config import write_summary


def _csv_block(df, n=5):
    return ["```", df.head(n).to_string(), "```"]


def run(cfg):
    raw = cfg["paths"]["raw"]
    lines = ["# Inspect summary", ""]
    files = sorted(p for p in raw.rglob("*") if p.is_file() and p.name != ".gitkeep")
    if not files:
        lines.append("No raw files. Run `python run.py fetch` first.")
    for p in files:
        rel = p.relative_to(raw)
        lines += [f"## {rel}", ""]
        if p.suffix == ".csv":
            df = pd.read_csv(p)
            lines.append(f"shape: {df.shape}")
            lines.append("columns / dtype / n_missing:")
            lines.append("```")
            for c in df.columns:
                lines.append(f"{c!r:40s} {str(df[c].dtype):10s} {df[c].isna().sum()}")
            lines.append("```")
            lines += ["head:"] + _csv_block(df) + ["tail:", "```", df.tail(3).to_string(), "```"]
            # anything that looks like a disease column: show distinct values
            for c in df.columns:
                if "disease" in c.lower() or "type" in c.lower():
                    vals = df[c].astype(str).unique()
                    lines.append(f"distinct `{c}` ({len(vals)}):")
                    lines += ["```", "\n".join(sorted(vals)), "```"]
        elif p.suffix == ".geojson":
            gj = json.loads(p.read_text(encoding="utf-8"))
            feats = gj.get("features", [])
            lines.append(f"features: {len(feats)}")
            if feats:
                props = pd.DataFrame([f["properties"] for f in feats])
                lines.append(f"property keys: {list(props.columns)}")
                if "CASE_SIZE" in props:
                    lines.append(f"total CASE_SIZE: {props.CASE_SIZE.sum()}, "
                                 f"max: {props.CASE_SIZE.max()}")
        else:
            lines.append(f"(unhandled type, {p.stat().st_size} bytes)")
        lines.append("")
    for l in lines[:60]:
        print(l)
    write_summary(cfg, "inspect", lines)
