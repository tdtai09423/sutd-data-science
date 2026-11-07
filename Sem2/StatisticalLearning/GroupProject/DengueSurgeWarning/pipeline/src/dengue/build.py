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


def load_cases_moh1418(path):
    """MOH 'Weekly Number of Dengue and DHF Cases' 2014-2018: year, eweek, type_dengue, number."""
    df = pd.read_csv(path)
    # the file has an empty week-53 row for every year; only 2014 really has 53 MMWR weeks
    df = df[df["number"].notna()].copy()
    df["epi_week"] = df["year"].astype(str) + "-W" + df["eweek"].astype(int).map("{:02d}".format)
    df["series"] = df["type_dengue"].map(lambda s: "dhf" if "dhf" in s.lower() else "dengue_fever")
    wide = df.pivot_table(index="epi_week", columns="series", values="number", aggfunc="sum")
    wide["cases"] = wide.sum(axis=1, min_count=1)
    wide = wide.reset_index().rename_axis(columns=None)
    wide["week_start"] = wide["epi_week"].map(epiweek_to_monday)
    return wide, sorted(df["type_dengue"].unique())


def load_case_source(raw, name, regex):
    path = raw / f"{name}.csv"
    if name == "moh_dengue_dhf_2014_2018":
        return load_cases_moh1418(path)
    return load_cases(path, regex)


def load_mss_daily(folder):
    """MSS monthly CSVs (one station) -> daily rain / temperature. Missing values are '-' or similar."""
    frames = []
    for f in sorted(folder.glob("*.csv")):
        d = pd.read_csv(f, encoding="latin1")
        # unit suffixes differ by file encoding ("(°C)" vs "(Â°C)"); keep only the name part
        d.columns = [c.replace("ï»¿", "").split("(")[0].strip().lower() for c in d.columns]
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    out = pd.DataFrame({"date": pd.to_datetime(dict(year=d.year, month=d.month, day=d.day))})
    for new, key in [("rain", "daily rainfall total"), ("temp_mean", "mean temperature"),
                     ("temp_max", "maximum temperature"), ("temp_min", "minimum temperature")]:
        out[new] = pd.to_numeric(d[key], errors="coerce")
    return out.drop_duplicates("date").sort_values("date").reset_index(drop=True)


def weekly_weather(daily, min_days=5):
    """Daily -> Mon-Sun weeks. Rain total = mean daily rain x 7 (so weeks with 1-2 missing days are
    not biased low); weeks with fewer than `min_days` observed days are set to missing."""
    w = daily.copy()
    w["week_start"] = w["date"] - pd.to_timedelta(w["date"].dt.weekday, unit="D")
    g = w.groupby("week_start")
    out = pd.DataFrame(index=g.size().index)
    if "rain" in w:
        n = g["rain"].count()
        out["rain_sum"] = (g["rain"].mean() * 7).where(n >= min_days)
        out["rain_days"] = (g["rain"].apply(lambda s: (s >= 1.0).mean()) * 7).where(n >= min_days)
    for c in ["temp_mean", "temp_max", "temp_min", "rh_mean"]:
        if c in w:
            out[c] = g[c].mean().where(g[c].count() >= min_days)
    return out[g.size() == 7].reset_index()   # drop incomplete calendar weeks at the edges


def build_weather(cfg, lines, tab):
    raw = cfg["paths"]["raw"]
    wc = cfg["weather"]
    om = pd.read_csv(raw / "weather_open_meteo_daily.csv", parse_dates=["date"]).rename(columns={
        "precipitation_sum": "rain", "temperature_2m_mean": "temp_mean", "temperature_2m_max": "temp_max",
        "temperature_2m_min": "temp_min", "relative_humidity_2m_mean": "rh_mean"})
    om_w = weekly_weather(om)
    if wc.get("source", "open_meteo") != "mss":
        lines.append("weather source: Open-Meteo reanalysis (all variables)")
        return om_w
    mss = load_mss_daily(raw / "mss" / wc["mss"]["station"])
    miss = mss.drop(columns="date").isna().sum()
    lines += [f"weather source: MSS station {wc['mss']['station']} (rain, temperature) "
              f"{mss.date.min().date()} -> {mss.date.max().date()}, {len(mss)} days; "
              f"humidity: {wc.get('humidity_source', 'open_meteo')}",
              "MSS missing days per variable: " + ", ".join(f"{k}={v}" for k, v in miss.items())]
    ms_w = weekly_weather(mss)
    w = ms_w.merge(om_w[["week_start", "rh_mean"]], on="week_start", how="left")

    # cross-checks: MSS vs reanalysis (weekly), reanalysis RH vs NEA monthly RH at Changi
    rows = []
    both = ms_w.merge(om_w, on="week_start", suffixes=("_mss", "_om"))
    for v in ["rain_sum", "temp_mean", "temp_max", "temp_min"]:
        a, b = both[f"{v}_mss"], both[f"{v}_om"]
        m = a.notna() & b.notna()
        rows.append({"check": f"weekly {v}: MSS vs Open-Meteo", "n": int(m.sum()),
                     "corr": a[m].corr(b[m]), "mean_diff": (b[m] - a[m]).mean()})
    rh_path = raw / "nea_rh_monthly.csv"
    if rh_path.exists():
        nea = pd.read_csv(rh_path)
        nea["month"] = pd.PeriodIndex(nea["month"], freq="M")
        omm = om.assign(month=om.date.dt.to_period("M")).groupby("month").rh_mean.mean()
        j = nea.set_index("month").join(omm, how="inner").dropna()
        rows.append({"check": "monthly RH: Open-Meteo vs NEA Changi", "n": len(j),
                     "corr": j.mean_rh.corr(j.rh_mean), "mean_diff": (j.rh_mean - j.mean_rh).mean()})
    chk = pd.DataFrame(rows)
    chk.round(3).to_csv(tab / "weather_crosscheck.csv", index=False)
    lines += ["", "weather cross-checks (corr, mean difference second - first):", "```",
              chk.round(3).to_string(index=False), "```"]
    return w


def quality_checks(df, lines):
    """Outliers / measurement checks on the weekly table (flags only, nothing is removed)."""
    lg = np.log1p(df["cases"]).diff()
    jumps = df.loc[lg.abs() > 0.5, ["week_start", "cases"]].assign(log_change=lg[lg.abs() > 0.5].round(2))
    lines += ["", f"weeks with |week-on-week log change| > 0.5 (possible reporting artefacts): {len(jumps)}",
              "```", jumps.to_string(index=False) if len(jumps) else "none", "```"]
    bounds = {"rain_sum": (0, 600), "temp_mean": (22, 32), "temp_max": (24, 38), "temp_min": (19, 30),
              "rh_mean": (50, 100)}
    bad = {k: int(((df[k] < lo) | (df[k] > hi)).sum()) for k, (lo, hi) in bounds.items() if k in df}
    lines.append(f"weather values outside plausible ranges {bounds}: {bad}")


def run(cfg):
    raw, proc = cfg["paths"]["raw"], cfg["paths"]["processed"]
    tab = cfg["paths"]["outputs"] / "tables"
    bc = cfg["build"]
    src = bc.get("case_source", "moh_weekly_bulletin")
    lines = ["# Build summary", "", f"case source: {src}"]

    cases, diseases = load_case_source(raw, src, bc["dengue_regex"])
    lines.append(f"dengue series used: {diseases}")
    dup = cases["week_start"].duplicated(keep=False)
    lines.append(f"duplicated epi weeks: {int(dup.sum())}")
    if dup.any():
        lines.append(f"WARNING duplicated week_start after parsing: "
                     f"{cases.loc[dup, 'epi_week'].tolist()}")
        cases = cases.groupby("week_start", as_index=False).agg(
            {c: "sum" if c != "epi_week" else "first" for c in cases.columns if c != "week_start"})

    full = pd.DataFrame({"week_start": pd.date_range(cases.week_start.min(),
                                                     cases.week_start.max(), freq="W-MON")})
    df = full.merge(cases, on="week_start", how="left")
    missing = df.loc[df["cases"].isna(), "week_start"].dt.date.tolist()
    lines.append(f"weeks: {len(df)} ({df.week_start.min().date()} -> {df.week_start.max().date()}), "
                 f"epi weeks per year: {df.groupby(df.week_start.dt.year).size().to_dict()}")
    lines.append(f"weeks with missing cases: {len(missing)} {missing[:20]}")

    xs = bc.get("crosscheck_source")
    if xs and xs != src and (raw / f"{xs}.csv").exists():
        other, _ = load_case_source(raw, xs, bc["dengue_regex"])
        cols = [c for c in ["dengue_fever", "dhf"] if c in df and c in other]
        j = df[["week_start", "epi_week"] + cols].merge(other[["week_start"] + cols], on="week_start",
                                                       suffixes=("", "_other"))
        rows = []
        for c in cols:
            diff = j[f"{c}_other"] - j[c]
            rows.append({"series": c, "overlap_weeks": len(j), "identical_weeks": int((diff == 0).sum()),
                         "max_abs_diff": diff.abs().max(), "total_main": j[c].sum(),
                         "total_other": j[f"{c}_other"].sum()})
        x = pd.DataFrame(rows)
        x.to_csv(tab / "case_crosscheck.csv", index=False)
        j.to_csv(tab / "case_crosscheck_weekly.csv", index=False)
        lines += ["", f"cross-check against {xs} on overlapping weeks (revisions between releases):",
                  "```", x.to_string(index=False), "```"]

    if (raw / "weather_open_meteo_daily.csv").exists():
        ww = build_weather(cfg, lines, tab)
        df = df.merge(ww, on="week_start", how="left")
        # keep weather weeks before the first case week too (for lags) in a separate file
        ww.to_csv(proc / "weather_weekly.csv", index=False)
        lines.append(f"weather weeks: {len(ww)} ({ww.week_start.min().date()} -> {ww.week_start.max().date()})")
    else:
        lines.append("WARNING: no weather file, building cases only")

    quality_checks(df, lines)
    df.to_csv(proc / "weekly.csv", index=False)
    lines += ["", "missing values per column:", "```", df.isna().sum().to_string(), "```",
              "", "describe:", "```", df.describe().T.round(2).to_string(), "```",
              "", "yearly totals:", "```",
              df.groupby(df.week_start.dt.year)["cases"].agg(["sum", "max", "mean"]).round(1).to_string(),
              "```"]
    for l in lines[:40]:
        print(l)
    write_summary(cfg, "build", lines)
