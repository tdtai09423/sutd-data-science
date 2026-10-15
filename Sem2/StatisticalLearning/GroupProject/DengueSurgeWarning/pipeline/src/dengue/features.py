"""Stage `features`: lagged predictors (known at week t) + surge target definitions.

Targets (all defined before any model is fitted, y = weekly dengue fever cases, DHF excluded):
  thr   y[t+h] > mean + k*sd of the past `window` weeks (known at t)
  seas  y[t+h] > q-th percentile of the same season (+-season_halfwidth days) in earlier
        seasons, using only weeks more than `exclude_recent_days` before t+h (known at t)
  grow  y[t+h] >= (1+pct[h])*y[t] and y[t+h] >= min_cases (week-on-week style rise)
  <kind>onset  same as thr / seas but only for weeks where y[t] is NOT already above its
        threshold (NaN otherwise): a true early warning, not persistence.
For every target, `fthr_<kind>_h<h>` holds the threshold y[t+h] must cross; it is known at t
and lets count regressions be turned into probabilities of crossing it."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import write_summary


def feature_groups(columns):
    cols = list(columns)
    case = [c for c in cols if c.startswith(("logy", "growth_", "marg_"))]
    season = [c for c in cols if c.startswith("woy_")]
    weather = [c for c in cols if "_lag" in c and not c.startswith("logy")]
    return {"cases": case + season, "weather": weather + season, "full": case + season + weather}


def target_columns(columns):
    return [c for c in columns if c.startswith("surge_")]


def parse_target(t):
    """'surge_thronset_h2' -> ('thronset', 'thr', 2)."""
    kind, h = t.split("_")[1], int(t.split("_h")[1])
    return kind, kind.replace("onset", ""), h


def seasonal_threshold(dates, y, q, halfwidth_days, exclude_recent_days, min_years):
    """For each week: q-quantile of y in the same season of earlier years, using only weeks
    older than `exclude_recent_days` (so the value for week t+h is already known at week t)."""
    doy = dates.dt.dayofyear.values
    out = np.full(len(y), np.nan)
    for i in range(len(y)):
        age = (dates.iloc[i] - dates).dt.days.values
        dd = np.abs(doy - doy[i])
        dd = np.minimum(dd, 365 - dd)
        m = (age > exclude_recent_days) & (dd <= halfwidth_days) & np.isfinite(y)
        if dates[m].dt.year.nunique() >= min_years:
            out[i] = np.quantile(y[m], q)
    return out


def build_table(cfg, df):
    fc, tc = cfg["features"], cfg["targets"]
    src = cfg["build"].get("target_series", "cases")
    keep = ["week_start", src] + [c for c in ["cases", "dhf"] if c in df and c != src]
    d = df[keep].copy().sort_values("week_start").reset_index(drop=True)
    d = d.rename(columns={"cases": "cases_total"}).rename(columns={src: "cases"})
    y = d["cases"]

    # thresholds (needed both for targets and for "distance to threshold" predictors)
    win, k = tc["threshold"]["window"], tc["threshold"]["k"]
    d["thr_mu"] = y.rolling(win, min_periods=win).mean()   # uses weeks t-win+1..t only
    d["thr_sd"] = y.rolling(win, min_periods=win).std()
    d["thr_now"] = d.thr_mu + k * d.thr_sd
    sc = tc["seasonal"]
    d["seas_now"] = seasonal_threshold(d.week_start, y.values.astype(float), sc["q"],
                                       sc["halfwidth_days"], sc["exclude_recent_days"], sc["min_years"])

    # case predictors; with report_delay=r, week t's own counts are treated as unknown
    r = fc.get("report_delay", 0)
    logy = np.log1p(y)
    d["logy"] = logy.shift(r)
    for L in fc["case_lags"]:
        d[f"logy_lag{L}"] = logy.shift(L + r)
    for w in fc["rolling_windows"]:
        d[f"logy_rm{w}"] = logy.rolling(w).mean().shift(r)
    d["growth_1"] = (logy - logy.shift(1)).shift(r)
    d["growth_4"] = (logy - logy.shift(4)).shift(r)
    d["marg_thr"] = (logy - np.log1p(d.thr_now)).shift(r)    # >0: already above threshold A
    d["marg_seas"] = (logy - np.log1p(d.seas_now)).shift(r)  # >0: already above seasonal p-tile
    d["woy"] = d["week_start"].dt.isocalendar().week.astype(int)
    d["woy_sin"], d["woy_cos"] = np.sin(2 * np.pi * d.woy / 52.18), np.cos(2 * np.pi * d.woy / 52.18)

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
    pct, mn = tc["growth"]["pct"], tc["growth"]["min_cases"]
    for h in tc["horizons"]:
        yf = y.shift(-h)
        d[f"y_fut_h{h}"] = yf
        p = pct[h] if isinstance(pct, dict) else pct   # pct may be set per horizon
        fthr = {"thr": d.thr_now, "seas": d.seas_now.shift(-h),
                "grow": np.maximum((1 + p) * y, mn)}
        now = {"thr": d.thr_now, "seas": d.seas_now}
        for kind, f in fthr.items():
            d[f"fthr_{kind}_h{h}"] = f
            lab = (yf >= f) if kind == "grow" else (yf > f)
            d[f"surge_{kind}_h{h}"] = lab.astype(float).where(yf.notna() & f.notna())
        for kind in tc.get("onset", []):
            below = y <= now[kind]
            d[f"surge_{kind}onset_h{h}"] = d[f"surge_{kind}_h{h}"].where(below)
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
    lines += ["```", "", "agreement between definitions (Jaccard of surge weeks, same horizon):", "```"]
    for h in cfg["targets"]["horizons"]:
        pairs = [("thr", "seas"), ("thr", "grow"), ("seas", "grow")]
        js = []
        for a_, b_ in pairs:
            a, b = d[f"surge_{a_}_h{h}"], d[f"surge_{b_}_h{h}"]
            m = a.notna() & b.notna()
            js.append(f"{a_}-{b_}={((a[m] == 1) & (b[m] == 1)).sum() / max(((a[m] == 1) | (b[m] == 1)).sum(), 1):.2f}")
        lines.append(f"h={h}  " + "  ".join(js))
    lines.append("```")
    if "dhf" in d:
        yr = d.groupby(d.week_start.dt.year).agg(df=("cases", "sum"), dhf=("dhf", "sum"))
        yr["dhf_share_pct"] = (100 * yr.dhf / (yr.df + yr.dhf)).round(2)
        lines += ["", f"target series: `{cfg['build'].get('target_series', 'cases')}` "
                  "(DHF kept separate; too rare to model on its own)", "```", yr.to_string(), "```"]

    # plot targets on top of the series (h = smallest horizon)
    h = cfg["targets"]["horizons"][0]
    fig, ax = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    for a, name in zip(ax, ["thr", "seas", "grow"]):
        a.plot(d.week_start, d.cases, lw=1, color="k")
        lab = d[f"surge_{name}_h{h}"] == 1
        a.scatter(d.week_start[lab], d.cases[lab], s=8, color="C3", label=f"surge_{name}_h{h}=1")
        a.legend(loc="upper left", fontsize=8)
    ax[0].plot(d.week_start, d.thr_now, color="C0", lw=.8, label="threshold")
    ax[1].plot(d.week_start, d.seas_now, color="C0", lw=.8, label="seasonal percentile")
    fig.tight_layout(); fig.savefig(out / "figures" / "features_targets.png", dpi=130); plt.close(fig)
    lines.append("figure: features_targets.png")
    for l in lines:
        print(l)
    write_summary(cfg, "features", lines)
