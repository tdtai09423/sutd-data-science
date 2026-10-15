"""Build the summary figures in visualize/ from pipeline outputs.

Run after `python run.py all`:
    pipeline/.venv/bin/python visualize/make_visuals.py
"""
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / "pipeline"
TAB = PIPE / "outputs/tables"
OUT = Path(__file__).resolve().parent
FIG = OUT / "figures"
shutil.rmtree(FIG, ignore_errors=True)
FIG.mkdir()

cfg = yaml.safe_load(open(PIPE / "config.yaml"))
H = cfg["targets"]["horizons"]
K = cfg["targets"]["threshold"]["k"]
Q = cfg["targets"]["seasonal"]["q"]
FIRST_TEST = cfg["model"]["first_test_year"]
COST = cfg["model"]["cost_ratio"]

pooled = pd.read_csv(TAB / "model_cv_pooled.csv")
by_year = pd.read_csv(TAB / "model_cv_by_year.csv")
imp = pd.read_csv(TAB / "feature_importance.csv")
cost = pd.read_csv(TAB / "alarm_cost_tradeoff.csv")
mt = pd.read_csv(PIPE / "data/processed/model_table.csv", parse_dates=["week_start"])
sens_path = TAB / "delay_sensitivity.csv"

BASE = ["thr", "seas", "grow"]
KIND_NAME = {"thr": "A threshold", "seas": "S seasonal p90", "grow": "B growth",
             "thronset": "A-onset", "seasonset": "S-onset"}
NICE = {"prior[woy]": "prior (base rate)", "seasonal[woy]": "seasonal baseline",
        "persistence[persist]": "persistence baseline", "logit[cases]": "logistic, cases",
        "logit[weather]": "logistic, weather", "logit[full]": "logistic, cases+weather",
        "lasso_logit[full]": "lasso logistic (CV)", "cart_d3[full]": "CART depth 3",
        "random_forest[full]": "random forest", "poisson_glm[full]": "Poisson GLM",
        "ridge_logcount[full]": "ridge on log counts"}
BASELINES = ["prior[woy]", "seasonal[woy]", "persistence[persist]"]
pooled["nice"] = pooled.model.map(NICE).fillna(pooled.model)


def tname(t):
    kind, h = t.split("_")[1], t.split("_h")[1]
    return f"{KIND_NAME[kind]}, h={h}"


plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False})


# 1. series, the three surge definitions, and DHF ---------------------------
fig, ax = plt.subplots(4, 1, figsize=(12, 9.5), sharex=True,
                       gridspec_kw={"height_ratios": [3, 3, 3, 1.2]})
tgt = mt.week_start + pd.Timedelta(weeks=1)
for a, kind, title, line in [
        (ax[0], "thr", f"A threshold: y[t+1] > mean + {K}·sd of past 52 weeks", "thr_now"),
        (ax[1], "seas", f"S seasonal: y[t+1] > {int(Q * 100)}th percentile of same season in earlier years",
         "seas_now"),
        (ax[2], "grow", "B growth: y[t+1] ≥ (1+pct)·y[t] and ≥ 50 cases", None)]:
    a.plot(mt.week_start, mt.cases, color="0.25", lw=1)
    lab = mt[f"surge_{kind}_h1"] == 1
    a.scatter(tgt[lab], mt.y_fut_h1[lab], s=9, color="#d62728", zorder=3, label="surge week")
    if kind in ("thr", "seas"):
        on = mt[f"surge_{kind}onset_h1"] == 1
        a.scatter(tgt[on], mt.y_fut_h1[on], s=40, facecolors="none", edgecolors="k", zorder=4,
                  label="onset (not yet above at t)")
    if line:
        a.plot(mt.week_start, mt[line], color="#1f77b4", lw=1, ls="--", label="threshold")
    a.axvline(pd.Timestamp(f"{FIRST_TEST}-01-01"), color="0.5", ls=":")
    a.set_title(title, loc="left", fontsize=10)
    a.set_ylabel("DF cases / wk")
    a.legend(loc="upper left", fontsize=7, frameon=False, ncol=3)
ax[3].bar(mt.week_start, mt.dhf, width=6, color="#9467bd")
ax[3].set_ylabel("DHF / wk")
ax[3].set_title("Dengue haemorrhagic fever (kept separate, too rare to model)", loc="left", fontsize=10)
fig.suptitle("Singapore weekly dengue fever cases 2012–2022 and surge labels (test period after dotted line)",
             x=0.01, ha="left")
fig.tight_layout()
fig.savefig(FIG / "01_cases_and_surge_definitions.png")
plt.close(fig)


# 2. PR-AUC with bootstrap CI, h=1, base targets ----------------------------
order = list(NICE)
fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
for a, kind in zip(axes, BASE):
    t = f"surge_{kind}_h1"
    g = pooled[pooled.target == t].set_index("model").reindex(order).dropna(subset=["pr_auc"])
    yy = np.arange(len(g))[::-1]
    col = ["0.55" if m in BASELINES else "#1f77b4" for m in g.index]
    a.errorbar(g.pr_auc, yy, xerr=[g.pr_auc - g.pr_auc_lo, g.pr_auc_hi - g.pr_auc], fmt="none",
               ecolor="0.6", lw=1)
    a.scatter(g.pr_auc, yy, c=col, zorder=3)
    a.axvline(g.prevalence.iloc[0], color="k", ls=":", lw=1)
    p = g.loc["persistence[persist]", "pr_auc"] if "persistence[persist]" in g.index else np.nan
    a.axvline(p, color="#d62728", ls="--", lw=1)
    a.set_yticks(yy, [NICE[m] for m in g.index], fontsize=8)
    a.set_title(tname(t), loc="left", fontsize=10)
    a.set_xlabel("PR-AUC (95% block-bootstrap CI)")
    a.set_xlim(0, 1)
fig.suptitle(f"Next-week surge (h=1): out-of-sample {FIRST_TEST}–2022   "
             "(dotted = no skill; red dashed = persistence; grey = baselines)", x=0.01, ha="left")
fig.tight_layout()
fig.savefig(FIG / "02_pr_auc_ci_h1.png")
plt.close(fig)


# 3. heatmap: gain over persistence, all targets ----------------------------
targets = [f"surge_{k}_h{h}" for k in ["thr", "thronset", "seas", "seasonset", "grow"] for h in H]
targets = [t for t in targets if t in set(pooled.target)]
piv = pooled.pivot_table(index="model", columns="target", values="pr_auc").reindex(order)[targets]
gain = piv - piv.loc["persistence[persist]"]
fig, ax = plt.subplots(figsize=(14, 5.5))
lim = np.nanmax(np.abs(gain.values))
im = ax.imshow(gain.values, cmap="RdBu", vmin=-lim, vmax=lim, aspect="auto")
for i in range(piv.shape[0]):
    for j in range(piv.shape[1]):
        v = piv.values[i, j]
        if np.isfinite(v):
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7)
pos = pooled.groupby("target").positives.first()
ax.set_xticks(range(len(targets)), [f"{tname(t)}\n(pos {pos[t]})" for t in targets], fontsize=7, rotation=45,
              ha="right")
ax.set_yticks(range(len(piv)), [NICE[m] for m in piv.index], fontsize=8)
ax.set_title("PR-AUC (numbers) and gain over persistence baseline (colour: blue = better, red = worse)",
             loc="left", fontsize=10)
fig.colorbar(im, ax=ax, shrink=0.8, label="PR-AUC − persistence")
fig.tight_layout()
fig.savefig(FIG / "03_pr_auc_vs_persistence_all_targets.png")
plt.close(fig)


# 4. PR-AUC by horizon ------------------------------------------------------
show = ["persistence[persist]", "seasonal[woy]", "logit[cases]", "lasso_logit[full]",
        "random_forest[full]", "poisson_glm[full]", "logit[weather]"]
kinds = ["thr", "thronset", "seas", "seasonset", "grow"]
fig, axes = plt.subplots(1, 5, figsize=(18, 4), sharey=True)
for a, kind in zip(axes, kinds):
    ts = [f"surge_{kind}_h{h}" for h in H]
    for m in show:
        y = [pooled.query("target == @t and model == @m").pr_auc.squeeze() for t in ts]
        a.plot(H, y, marker="o", label=NICE[m], ls="--" if m in BASELINES else "-")
    a.plot(H, [pooled.query("target == @t").prevalence.iloc[0] for t in ts], color="k", ls=":",
           label="no skill")
    a.set_xticks(H)
    a.set_title(KIND_NAME[kind], loc="left", fontsize=10)
    a.set_xlabel("horizon h (weeks)")
axes[0].set_ylabel("PR-AUC")
axes[-1].legend(fontsize=7, frameon=False, bbox_to_anchor=(1, 1), loc="upper left")
fig.tight_layout()
fig.savefig(FIG / "04_pr_auc_by_horizon.png")
plt.close(fig)


# 5. calibration (from pipeline) --------------------------------------------
shutil.copy(PIPE / "outputs/figures/model_calibration.png", FIG / "05_calibration_h1.png")


# 6. operational trade-off: recall vs alarms per year -----------------------
fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), sharey=True)
for a, kind in zip(axes, BASE):
    t = f"surge_{kind}_h1"
    for m in ["persistence[persist]", "seasonal[woy]", "logit[cases]", "lasso_logit[full]", "poisson_glm[full]"]:
        g = cost[(cost.target == t) & (cost.model == m)].sort_values("cost_ratio")
        a.plot(g.alarms_per_year, g.recall, marker="o", label=NICE[m], ls="--" if m in BASELINES else "-")
        for _, r in g.iterrows():
            if m == "lasso_logit[full]":
                a.annotate(f"{int(r.cost_ratio)}:1", (r.alarms_per_year, r.recall), fontsize=7,
                           xytext=(3, -8), textcoords="offset points")
    a.set_title(tname(t), loc="left", fontsize=10)
    a.set_xlabel("alarms per year")
axes[0].set_ylabel("recall (share of surge weeks flagged)")
axes[-1].legend(fontsize=7, frameon=False)
fig.suptitle("Cost of false alarms: each point is a cost ratio miss:false-alarm (1, 2, 4, 9)", x=0.01, ha="left")
fig.tight_layout()
fig.savefig(FIG / "06_alarm_tradeoff_h1.png")
plt.close(fig)


# 7. stability by test year -------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
for a, kind in zip(axes, BASE):
    t = f"surge_{kind}_h1"
    for m in ["persistence[persist]", "seasonal[woy]", "logit[cases]", "lasso_logit[full]", "random_forest[full]"]:
        g = by_year[(by_year.target == t) & (by_year.model == m)]
        a.plot(g.year, g.pr_auc, marker="o", label=NICE[m], ls="--" if m in BASELINES else "-")
    a.set_title(f"{tname(t)}: PR-AUC by test year", loc="left", fontsize=10)
    a.set_xlabel("year")
axes[0].set_ylabel("PR-AUC")
axes[-1].legend(fontsize=7, frameon=False)
fig.tight_layout()
fig.savefig(FIG / "07_pr_auc_by_year_h1.png")
plt.close(fig)


# 8. top features (full-sample lasso and RF), h=1 ---------------------------
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for a, kind in zip(axes, BASE):
    t = f"surge_{kind}_h1"
    g = imp[imp.target == t].sort_values("rf_importance", ascending=False).head(12)[::-1]
    yy = np.arange(len(g))
    a.barh(yy - 0.2, g.rf_importance / g.rf_importance.max(), height=0.4, label="random forest (scaled)")
    a.barh(yy + 0.2, g.abs_coef / max(g.abs_coef.max(), 1e-9), height=0.4, label="lasso |std. coef| (scaled)")
    a.set_yticks(yy, g.feature, fontsize=8)
    a.set_title(f"{tname(t)}: top 12 predictors", loc="left", fontsize=10)
axes[0].legend(fontsize=8, frameon=False, loc="lower right")
fig.tight_layout()
fig.savefig(FIG / "08_top_features_h1.png")
plt.close(fig)


# 9. reporting-delay sensitivity --------------------------------------------
if sens_path.exists():
    s = pd.read_csv(sens_path)
    s["label"] = s.target.map(tname) + " | " + s.model.map(NICE)
    s = s.sort_values(["target", "delay0"])
    fig, ax = plt.subplots(figsize=(9, 0.32 * len(s) + 1))
    yy = np.arange(len(s))
    ax.hlines(yy, s.delay1, s.delay0, color="0.6")
    ax.scatter(s.delay0, yy, label="counts of week t available", zorder=3)
    ax.scatter(s.delay1, yy, label="1-week reporting delay", zorder=3)
    ax.set_yticks(yy, s.label, fontsize=7)
    ax.set_xlabel("PR-AUC")
    ax.legend(fontsize=8, frameon=False)
    ax.set_title("Sensitivity to case reporting delay (h=1)", loc="left", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "09_reporting_delay_sensitivity.png")
    plt.close(fig)

# EDA figures worth keeping -------------------------------------------------
for src, dst in [("eda_seasonality.png", "10a_eda_seasonality.png"),
                 ("eda_lagged_corr.png", "10b_eda_weather_lag_corr.png"),
                 ("eda_cases_vs_weather.png", "10c_eda_cases_vs_weather.png")]:
    shutil.copy(PIPE / "outputs/figures" / src, FIG / dst)
for f in sorted((PIPE / "outputs/figures").glob("model_best_*_h1.png")):
    shutil.copy(f, FIG / f"11_{f.name}")

# key numbers ---------------------------------------------------------------
rows = []
for t in targets:
    g = pooled[pooled.target == t]
    best = g[~g.model.isin(BASELINES)].sort_values("pr_auc", ascending=False).iloc[0]
    per = g[g.model == "persistence[persist]"].iloc[0]
    sea = g[g.model == "seasonal[woy]"].iloc[0]
    rows.append({"target": t, "positives": best.positives, "prevalence": best.prevalence,
                 "seasonal_pr_auc": sea.pr_auc, "persistence_pr_auc": per.pr_auc,
                 "best_model": best.model, "best_pr_auc": best.pr_auc,
                 "best_ci": f"[{best.pr_auc_lo:.2f}, {best.pr_auc_hi:.2f}]",
                 "p_best_beats_persistence": best.p_better_than_persistence,
                 "best_brier": best.brier, "best_recall": best.recall,
                 "best_precision": best.precision, "best_alarms_per_year": best.alarms_per_year})
key = pd.DataFrame(rows).round(3)
key.to_csv(OUT / "key_results.csv", index=False)
print(key.to_string(index=False))
