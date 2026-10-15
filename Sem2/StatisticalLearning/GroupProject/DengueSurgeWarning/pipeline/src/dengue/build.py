"""Stage `build`: weekly national table = dengue cases + weekly weather."""
import datetime as dt
import re

import numpy as np
import pandas as pd

from .config import write_summary


def _find(df, *keys):
    for c in df.columns:
        if any(k in c.lower() for k in keys):
            return c
    raise KeyError(f"no column containing {keys} in {list(df.columns)}")


def epiweek_to_monday(s):
    """'2012-W01' -> Monday after the Sunday that starts that epi week.
    Singapore epi weeks run Sun-Sat (MMWR rule: week 1 is the Sun-Sat week containing
    4 Jan). This differs from ISO in which years have 53 weeks (e.g. 2014 vs 2015), so
    ISO numbering must not be used. Shifting to Monday keeps the weather keys aligned."""
    m = re.match(r"(\d{4})\D*W?(\d{1,2})", str(s))
    if not m:
        return pd.NaT
    y, w = int(m.group(1)), int(m.group(2))
    jan4 = dt.date(y, 1, 4)
    week1_sunday = jan4 - dt.timedelta(days=(jan4.weekday() + 1) % 7)
    return pd.Timestamp(week1_sunday + dt.timedelta(days=7 * (w - 1) + 1))


def _snake(name):
    n = name.lower()
    if "haemorrhagic" in n or "hemorrhagic" in n or n.strip() == "dhf":
        return "dhf"
    return re.sub(r"[^a-z0-9]+", "_", n).strip("_")


def load_cases(path, regex):
    df = pd.read_csv(path)
    wk, dis, cs = _find(df, "week"), _find(df, "disease"), _find(df, "case")
    df = df.rename(columns={wk: "epi_week", dis: "disease", cs: "cases"})
    d = df[df["disease"].astype(str).str.contains(regex, case=False, na=False)].copy()
    d["cases"] = pd.to_numeric(d["cases"], errors="coerce")
    wide = d.pivot_table(index="epi_week", columns="disease", values="cases", aggfunc="sum")
    wide.columns = [_snake(c) for c in wide.columns]
    wide["cases"] = wide.sum(axis=1, min_count=1)
    wide = wide.reset_index()
    wide["week_start"] = wide["epi_week"].map(epiweek_to_monday)
    return wide, sorted(d["disease"].unique())


def load_weather_weekly(path):
    w = pd.read_csv(path, parse_dates=["date"])
    w["week_start"] = w["date"] - pd.to_timedelta(w["date"].dt.weekday, unit="D")
    rename = {
        "precipitation_sum": "rain", "temperature_2m_mean": "temp_mean",
        "temperature_2m_max": "temp_max", "temperature_2m_min": "temp_min",
        "relative_humidity_2m_mean": "rh_mean",
    }
    w = w.rename(columns=rename)
    agg = {}
    if "rain" in w:
        w["rain_day"] = (w["rain"] >= 1.0).astype(float)
        agg.update(rain_sum=("rain", "sum"), rain_days=("rain_day", "sum"))
    for c in ["temp_mean", "temp_max", "temp_min", "rh_mean"]:
        if c in w:
            agg[c] = (c, "mean")
    out = w.groupby("week_start").agg(**agg)
    out["n_days"] = w.groupby("week_start").size()
    return out[out["n_days"] == 7].drop(columns="n_days").reset_index()


def run(cfg):
    raw, proc = cfg["paths"]["raw"], cfg["paths"]["processed"]
    lines = ["# Build summary", ""]

    cases, diseases = load_cases(raw / "moh_weekly_bulletin.csv", cfg["build"]["dengue_regex"])
    lines.append(f"dengue diseases used: {diseases}")
    dup = cases["week_start"].duplicated(keep=False)
    if dup.any():
        lines.append(f"WARNING duplicated week_start after parsing: "
                     f"{cases.loc[dup, 'epi_week'].tolist()}")
        cases = cases.groupby("week_start", as_index=False).agg(
            {c: "sum" if c != "epi_week" else "first" for c in cases.columns if c != "week_start"})

    full = pd.DataFrame({"week_start": pd.date_range(cases.week_start.min(),
                                                     cases.week_start.max(), freq="W-MON")})
    df = full.merge(cases, on="week_start", how="left")
    missing = df.loc[df["cases"].isna(), "week_start"].dt.date.tolist()
    lines.append(f"weeks: {len(df)} ({df.week_start.min().date()} -> {df.week_start.max().date()})")
    lines.append(f"weeks with missing cases: {len(missing)} {missing[:20]}")

    wpath = raw / "weather_open_meteo_daily.csv"
    if wpath.exists():
        ww = load_weather_weekly(wpath)
        df = df.merge(ww, on="week_start", how="left")
        # keep weather weeks before the first case week too (for lags) in a separate file
        ww.to_csv(proc / "weather_weekly.csv", index=False)
        lines.append(f"weather weeks: {len(ww)} ({ww.week_start.min().date()} -> {ww.week_start.max().date()})")
    else:
        lines.append("WARNING: no weather file, building cases only")

    df.to_csv(proc / "weekly.csv", index=False)
    lines += ["", "missing values per column:", "```", df.isna().sum().to_string(), "```",
              "", "describe:", "```", df.describe().T.round(2).to_string(), "```",
              "", "yearly totals:", "```",
              df.groupby(df.week_start.dt.year)["cases"].agg(["sum", "max", "mean"]).round(1).to_string(),
              "```"]
    for l in lines[:30]:
        print(l)
    write_summary(cfg, "build", lines)
