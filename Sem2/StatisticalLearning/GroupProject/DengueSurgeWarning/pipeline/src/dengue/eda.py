"""Stage `eda`: plots + lagged correlations, to decide features and target thresholds."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import write_summary


def _weather_full(cfg, df):
    """Weather over the full fetched period (so lags before 2012 are available)."""
    p = cfg["paths"]["processed"] / "weather_weekly.csv"
    if p.exists():
        w = pd.read_csv(p, parse_dates=["week_start"])
        return df[["week_start", "cases"]].merge(w, on="week_start", how="right").sort_values("week_start")
    return df


def run(cfg):
    proc, out = cfg["paths"]["processed"], cfg["paths"]["outputs"]
    fig_dir, tab_dir = out / "figures", out / "tables"
    df = pd.read_csv(proc / "weekly.csv", parse_dates=["week_start"])
    lines = ["# EDA summary", ""]

    # 1. time series
    fig, ax = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    ax[0].plot(df.week_start, df.cases, lw=1)
    ax[0].set_ylabel("weekly cases")
    ax[1].plot(df.week_start, np.log1p(df.cases), lw=1)
    ax[1].set_ylabel("log(1+cases)")
    fig.suptitle("Singapore weekly dengue cases")
    fig.tight_layout(); fig.savefig(fig_dir / "eda_cases_timeseries.png", dpi=130); plt.close(fig)

    # 2. seasonality
    df["woy"] = df.week_start.dt.isocalendar().week.astype(int)
    fig, ax = plt.subplots(figsize=(12, 4))
    df.boxplot(column="cases", by="woy", ax=ax, showfliers=False)
    ax.set_title("cases by week of year"); ax.set_xlabel("ISO week"); fig.suptitle("")
    ax.set_xticks(range(1, 54, 4)); ax.set_xticklabels(range(1, 54, 4))
    fig.tight_layout(); fig.savefig(fig_dir / "eda_seasonality.png", dpi=130); plt.close(fig)

    yearly = df.groupby(df.week_start.dt.year)["cases"].agg(["sum", "max"])
    lines += ["yearly total / peak week:", "```", yearly.to_string(), "```", ""]

    # 3. lagged correlation with weather: level and growth
    wvars = [v for v in cfg["features"]["weather_vars"] if v in df.columns]
    if wvars:
        full = _weather_full(cfg, df)
        logy = np.log1p(full["cases"])
        growth = np.log1p(full["cases"].shift(-4)) - logy   # 4-week-ahead growth
        rows = []
        for v in wvars:
            for L in range(0, 21):
                x = full[v].shift(L)
                rows.append({"var": v, "lag": L,
                             "corr_level": logy.corr(x),
                             "corr_growth4": growth.corr(x)})
        ccf = pd.DataFrame(rows)
        ccf.to_csv(tab_dir / "eda_lagged_corr.csv", index=False)

        fig, axes = plt.subplots(1, 2, figsize=(13, 4), sharey=True)
        for v in wvars:
            s = ccf[ccf["var"] == v]
            axes[0].plot(s.lag, s.corr_level, marker=".", label=v)
            axes[1].plot(s.lag, s.corr_growth4, marker=".", label=v)
        axes[0].set_title("corr(log cases_t, weather_{t-lag})")
        axes[1].set_title("corr(4-wk growth from t, weather_{t-lag})")
        for a in axes:
            a.axhline(0, color="k", lw=.5); a.set_xlabel("lag (weeks)")
        axes[1].legend(fontsize=8)
        fig.tight_layout(); fig.savefig(fig_dir / "eda_lagged_corr.png", dpi=130); plt.close(fig)

        lines.append("strongest lag per weather var (by |corr|):")
        lines.append("```")
        for v in wvars:
            s = ccf[ccf["var"] == v]
            a = s.loc[s.corr_level.abs().idxmax()]
            b = s.loc[s.corr_growth4.abs().idxmax()]
            lines.append(f"{v:10s} level: lag {int(a.lag):2d} r={a.corr_level:+.2f} | "
                         f"growth4: lag {int(b.lag):2d} r={b.corr_growth4:+.2f}")
        lines += ["```", "NOTE: raw correlations are confounded by seasonality; treat as a guide only.", ""]

        # weather vs cases overlay
        fig, ax1 = plt.subplots(figsize=(12, 4))
        ax1.plot(df.week_start, df.cases, color="C3", lw=1, label="cases")
        ax2 = ax1.twinx()
        if "rain_sum" in df:
            ax2.plot(df.week_start, df.rain_sum.rolling(4).mean(), color="C0", lw=.8, label="rain (4w mean)")
        if "temp_mean" in df:
            ax3 = ax1.twinx(); ax3.spines["right"].set_position(("axes", 1.07))
            ax3.plot(df.week_start, df.temp_mean.rolling(4).mean(), color="C1", lw=.8, label="temp (4w mean)")
        fig.legend(loc="upper left", fontsize=8)
        fig.tight_layout(); fig.savefig(fig_dir / "eda_cases_vs_weather.png", dpi=130); plt.close(fig)

    # 4. autocorrelation of log cases
    logc = np.log1p(df["cases"])
    acf = [logc.autocorr(L) for L in range(1, 27)]
    lines += ["autocorrelation of log cases, lags 1..8: " +
              ", ".join(f"{a:.2f}" for a in acf[:8]), ""]
    lines.append("figures: " + ", ".join(p.name for p in sorted(fig_dir.glob("eda_*.png"))))
    for l in lines:
        print(l)
    write_summary(cfg, "eda", lines)
