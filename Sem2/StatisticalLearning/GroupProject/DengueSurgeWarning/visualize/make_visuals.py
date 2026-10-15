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
from sklearn.metrics import average_precision_score

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / "pipeline"
OUT = Path(__file__).resolve().parent
FIG = OUT / "figures"
FIG.mkdir(exist_ok=True)

cfg = yaml.safe_load(open(PIPE / "config.yaml"))
H = cfg["targets"]["horizons"]
K = cfg["targets"]["threshold"]["k"]
FIRST_TEST = cfg["model"]["first_test_year"]

pooled = pd.read_csv(PIPE / "outputs/tables/model_cv_pooled.csv")
folds = pd.read_csv(PIPE / "outputs/tables/model_cv_by_fold.csv")
imp = pd.read_csv(PIPE / "outputs/tables/feature_importance.csv")
mt = pd.read_csv(PIPE / "data/processed/model_table.csv", parse_dates=["week_start"])

pooled["label"] = pooled.model + " (" + pooled.features + ")"
TARGETS = [f"surge_{k}_h{h}" for k in ["thr", "grow"] for h in H]
NICE = {f"surge_thr_h{h}": f"A threshold, h={h}" for h in H}
NICE.update({f"surge_grow_h{h}": f"B growth, h={h}" for h in H})
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False})


# 1. case series with both surge labels -----------------------------------
fig, ax = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
for a, kind, title in [(ax[0], "thr", f"A: threshold (mean + {K}·sd of past 52 wk)"),
                       (ax[1], "grow", "B: growth vs current week")]:
    a.plot(mt.week_start, mt.cases, color="0.25", lw=1)
    lab = mt[f"surge_{kind}_h1"] == 1
    tgt = mt.week_start + pd.Timedelta(weeks=1)
    a.scatter(tgt[lab], mt.y_fut_h1[lab], s=10, color="#d62728", zorder=3, label="surge week (h=1)")
    if kind == "thr":
        a.plot(mt.week_start, mt.thr_mu + K * mt.thr_sd, color="#1f77b4", lw=1, ls="--",
               label="alarm threshold")
    a.axvline(pd.Timestamp(f"{FIRST_TEST}-01-01"), color="0.5", ls=":")
    a.set_title(title, loc="left", fontsize=10)
    a.set_ylabel("weekly cases")
    a.legend(loc="upper left", fontsize=8, frameon=False)
ax[1].text(pd.Timestamp(f"{FIRST_TEST}-02-01"), ax[1].get_ylim()[1] * 0.9, "test period →", fontsize=8)
fig.suptitle("Singapore weekly dengue cases (DF + DHF), 2012–2022, with surge labels", x=0.01, ha="left")
fig.tight_layout()
fig.savefig(FIG / "01_cases_and_surge_labels.png")
plt.close(fig)


# 2. PR-AUC heatmap: model x target --------------------------------------
piv = pooled.pivot_table(index="label", columns="target", values="pr_auc")[TARGETS]
piv = piv.loc[piv.mean(axis=1).sort_values(ascending=False).index]
prev = pooled.groupby("target").prevalence.first()[TARGETS]
fig, ax = plt.subplots(figsize=(9, 5.5))
im = ax.imshow(piv.values, cmap="Blues", vmin=0, vmax=1, aspect="auto")
for i in range(piv.shape[0]):
    for j in range(piv.shape[1]):
        v = piv.values[i, j]
        if np.isfinite(v):
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8,
                    color="white" if v > 0.6 else "black")
ax.set_xticks(range(len(TARGETS)), [f"{NICE[t]}\n(prev {prev[t]:.2f})" for t in TARGETS], fontsize=8)
ax.set_yticks(range(len(piv)), piv.index, fontsize=8)
ax.set_title("PR-AUC, rolling-origin CV 2017–2022 (higher is better; prevalence = no-skill level)",
             loc="left", fontsize=10)
fig.colorbar(im, ax=ax, shrink=0.8, label="PR-AUC")
fig.tight_layout()
fig.savefig(FIG / "02_pr_auc_heatmap.png")
plt.close(fig)


# 3. naive persistence baseline: "alarm if already above threshold today" --
def persistence_scores():
    rows = []
    for h in H:
        t = f"surge_thr_h{h}"
        d = mt.dropna(subset=[t, "thr_mu", "thr_sd"])
        d = d[d.week_start.dt.year >= FIRST_TEST]
        z = (d.cases - d.thr_mu) / d.thr_sd.replace(0, np.nan)
        rows.append({"target": t, "pr_auc": average_precision_score(d[t], z.fillna(0))})
    return pd.DataFrame(rows).set_index("target").pr_auc


persist = persistence_scores()

# 4. PR-AUC vs horizon: best model per family + baselines -----------------
fam = {"logit (cases)": "logistic, cases only", "logit (full)": "logistic, all features",
       "logit_l1 (full)": "lasso logistic", "poisson_glm (full)": "Poisson GLM → alarm",
       "tree_d3 (full)": "decision tree (depth 3)", "random_forest (full)": "random forest",
       "logit (weather)": "logistic, weather only"}
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
for a, kind in zip(axes, ["thr", "grow"]):
    ts = [f"surge_{kind}_h{h}" for h in H]
    for lab, nice in fam.items():
        y = [pooled.query("target == @t and label == @lab").pr_auc.squeeze() for t in ts]
        a.plot(H, y, marker="o", label=nice)
    a.plot(H, [prev[t] for t in ts], color="k", ls=":", label="no skill (prevalence)")
    if kind == "thr":
        a.plot(H, [persist[t] for t in ts], color="k", ls="--", marker="x",
               label="naive: z-score of current week")
    a.set_xticks(H)
    a.set_xlabel("forecast horizon h (weeks)")
    a.set_title("Target A: threshold" if kind == "thr" else "Target B: growth", loc="left")
axes[0].set_ylabel("PR-AUC (pooled 2017–2022)")
axes[1].legend(fontsize=8, frameon=False, loc="upper right")
fig.tight_layout()
fig.savefig(FIG / "03_pr_auc_by_horizon.png")
plt.close(fig)


# 5. PR-AUC per test year (stability) -------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
for a, t in zip(axes, ["surge_thr_h2", "surge_grow_h2"]):
    f = folds[folds.target == t].copy()
    f["label"] = f.model + " (" + f.features + ")"
    for lab in ["logit (cases)", "poisson_glm (full)", "logit_l1 (full)", "random_forest (full)",
                "prior (cases)"]:
        g = f[f.label == lab]
        a.plot(g.year, g.pr_auc, marker="o", label=fam.get(lab, "prior (base rate)"))
    a.set_title(f"{NICE[t]}: PR-AUC by test year", loc="left", fontsize=10)
    a.set_xlabel("test year")
axes[0].set_ylabel("PR-AUC")
axes[1].legend(fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(FIG / "05_pr_auc_by_year.png")
plt.close(fig)


# 6. top features (lasso |coef| and RF importance), h=2 --------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for a, t in zip(axes, ["surge_thr_h2", "surge_grow_h2"]):
    g = imp[imp.target == t].sort_values("rf_importance", ascending=False).head(12)[::-1]
    yy = np.arange(len(g))
    a.barh(yy - 0.2, g.rf_importance / g.rf_importance.max(), height=0.4, label="random forest (scaled)")
    a.barh(yy + 0.2, g.abs_coef / max(g.abs_coef.max(), 1e-9), height=0.4,
           label="lasso |std. coef| (scaled)")
    a.set_yticks(yy, g.feature, fontsize=8)
    a.set_title(f"{NICE[t]}: top 12 features", loc="left", fontsize=10)
axes[0].legend(fontsize=8, frameon=False, loc="lower right")
fig.tight_layout()
fig.savefig(FIG / "06_top_features_h2.png")
plt.close(fig)


# copy pipeline figures that are worth keeping -----------------------------
for src, dst in [("eda_seasonality.png", "04a_eda_seasonality.png"),
                 ("eda_lagged_corr.png", "04b_eda_weather_lag_corr.png"),
                 ("eda_cases_vs_weather.png", "04c_eda_cases_vs_weather.png"),
                 ("model_best_surge_thr_h2.png", "07a_best_model_thr_h2.png"),
                 ("model_best_surge_grow_h2.png", "07b_best_model_grow_h2.png")]:
    shutil.copy(PIPE / "outputs/figures" / src, FIG / dst)

# key numbers table ---------------------------------------------------------
best = (pooled[pooled.model != "prior"].sort_values("pr_auc", ascending=False)
        .groupby("target").head(1).set_index("target").loc[TARGETS])
key = pd.DataFrame({
    "prevalence": prev,
    "best_model": best.label,
    "best_pr_auc": best.pr_auc,
    "best_roc_auc": best.roc_auc,
    "precision@alarm": best.precision,
    "recall@alarm": best.recall,
    "naive_persistence_pr_auc": persist.reindex(TARGETS),
}).round(3)
key.to_csv(OUT / "key_results.csv")
print(key.to_string())
