"""Stage `features`: lagged predictors (known at week t) + two surge target definitions."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import write_summary


def feature_groups(columns):
    cols = list(columns)
    case = [c for c in cols if c.startswith(("logy", "growth_"))]
    season = [c for c in cols if c.startswith("woy_")]
    weather = [c for c in cols if "_lag" in c and not c.startswith("logy")]
    return {"cases": case + season, "weather": weather + season, "full": case + season + weather}


def target_columns(columns):
    return [c for c in columns if c.startswith("surge_")]


def build_table(cfg, df):
    fc, tc = cfg["features"], cfg["targets"]
    d = df[["week_start", "cases"]].copy().sort_values("week_start").reset_index(drop=True)
    y = d["cases"]
    d["logy"] = np.log1p(y)
    for L in fc["case_lags"]:
        d[f"logy_lag{L}"] = d["logy"].shift(L)
    for w in fc["rolling_windows"]:
        d[f"logy_rm{w}"] = d["logy"].rolling(w).mean()
    d["growth_1"] = d["logy"] - d["logy"].shift(1)
    d["growth_4"] = d["logy"] - d["logy"].shift(4)
    woy = d["week_start"].dt.isocalendar().week.astype(int)
    d["woy_sin"], d["woy_cos"] = np.sin(2 * np.pi * woy / 52.18), np.cos(2 * np.pi * woy / 52.18)

    # weather lags computed on the full weather history (starts before case data)
    wpath = cfg["paths"]["processed"] / "weather_weekly.csv"
    if wpath.exists():
        w = pd.read_csv(wpath, parse_dates=["week_start"]).set_index("week_start")
        w = w.reindex(pd.date_range(w.index.min(), max(w.index.max(), d.week_start.max()), freq="W-MON"))
        lagged = {}
        for v in fc["weather_vars"]:
            if v in w:
                for L in fc["weather_lags"]:
                    lagged[f"{v}_lag{L}"] = w[v].shift(L)
        lagged = pd.DataFrame(lagged).rename_axis("week_start").reset_index()
        d = d.merge(lagged, on="week_start", how="left")

    # targets -----------------------------------------------------------
    win, k = tc["threshold"]["window"], tc["threshold"]["k"]
    d["thr_mu"] = y.rolling(win, min_periods=win).mean()   # uses weeks t-win+1..t only
    d["thr_sd"] = y.rolling(win, min_periods=win).std()
    pct, mn = tc["growth"]["pct"], tc["growth"]["min_cases"]
    for h in tc["horizons"]:
        yf = y.shift(-h)
        d[f"y_fut_h{h}"] = yf
        thr = (yf > d.thr_mu + k * d.thr_sd).astype(float)
        d[f"surge_thr_h{h}"] = thr.where(yf.notna() & d.thr_mu.notna())
        p = pct[h] if isinstance(pct, dict) else pct   # pct may be set per horizon
        grow = ((yf >= (1 + p) * y) & (yf >= mn)).astype(float)
        d[f"surge_grow_h{h}"] = grow.where(yf.notna() & y.notna())
    return d


def run(cfg):
    proc, out = cfg["paths"]["processed"], cfg["paths"]["outputs"]
    df = pd.read_csv(proc / "weekly.csv", parse_dates=["week_start"])
    d = build_table(cfg, df)
    d.to_csv(proc / "model_table.csv", index=False)

    groups = feature_groups(d.columns)
    tcols = target_columns(d.columns)
    lines = ["# Features summary", "", f"rows: {len(d)}",
             f"feature groups: " + ", ".join(f"{k}={len(v)}" for k, v in groups.items()), ""]
    lines += ["target prevalence (share of weeks labelled surge) and n:", "```"]
    for t in tcols:
        s = d[t].dropna()
        lines.append(f"{t:18s} prevalence={s.mean():.3f}  n={len(s)}  positives={int(s.sum())}")
    lines += ["```", "", "agreement between definitions (same horizon):", "```"]
    for h in cfg["targets"]["horizons"]:
        a, b = d[f"surge_thr_h{h}"], d[f"surge_grow_h{h}"]
        m = a.notna() & b.notna()
        ct = pd.crosstab(a[m], b[m], rownames=["thr"], colnames=["grow"])
        jac = ((a[m] == 1) & (b[m] == 1)).sum() / max(((a[m] == 1) | (b[m] == 1)).sum(), 1)
        lines += [f"h={h}  Jaccard={jac:.2f}", ct.to_string(), ""]
    lines.append("```")

    # plot targets on top of the series (h = smallest horizon)
    h = cfg["targets"]["horizons"][0]
    fig, ax = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    for a, name in zip(ax, ["thr", "grow"]):
        a.plot(d.week_start, d.cases, lw=1, color="k")
        lab = d[f"surge_{name}_h{h}"] == 1
        a.scatter(d.week_start[lab], d.cases[lab], s=8, color="C3", label=f"surge_{name}_h{h}=1")
        a.legend(loc="upper left", fontsize=8)
    ax[0].plot(d.week_start, d.thr_mu + cfg["targets"]["threshold"]["k"] * d.thr_sd,
               color="C0", lw=.8, label="threshold")
    fig.tight_layout(); fig.savefig(out / "figures" / "features_targets.png", dpi=130); plt.close(fig)
    lines.append("figure: features_targets.png")
    for l in lines:
        print(l)
    write_summary(cfg, "features", lines)
