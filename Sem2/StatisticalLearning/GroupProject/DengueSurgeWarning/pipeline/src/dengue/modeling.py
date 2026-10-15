"""Stage `model`: rolling-origin CV comparing classifiers and count regressions for each target."""
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import (HistGradientBoostingClassifier, HistGradientBoostingRegressor,
                              RandomForestClassifier)
from sklearn.linear_model import LogisticRegression, PoissonRegressor
from sklearn.metrics import (average_precision_score, brier_score_loss, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text

from .config import write_summary
from .features import feature_groups, target_columns

warnings.filterwarnings("ignore", category=UserWarning)


def model_specs(rs):
    """(name, feature_set, kind, factory). kind: clf -> probability, reg -> count forecast."""
    return [
        ("prior", "cases", "clf", lambda: DummyClassifier(strategy="prior")),
        ("logit", "cases", "clf", lambda: make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000))),
        ("logit", "weather", "clf", lambda: make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000))),
        ("logit", "full", "clf", lambda: make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000))),
        ("logit_l1", "full", "clf", lambda: make_pipeline(StandardScaler(), LogisticRegression(
            penalty="l1", solver="liblinear", C=0.1, max_iter=5000))),
        ("tree_d3", "full", "clf", lambda: DecisionTreeClassifier(max_depth=3, min_samples_leaf=20, random_state=rs)),
        ("random_forest", "full", "clf", lambda: RandomForestClassifier(
            n_estimators=500, min_samples_leaf=5, n_jobs=-1, random_state=rs)),
        ("hist_gb", "full", "clf", lambda: HistGradientBoostingClassifier(
            max_depth=3, learning_rate=0.05, max_iter=300, random_state=rs)),
        ("poisson_glm", "full", "reg", lambda: make_pipeline(StandardScaler(), PoissonRegressor(alpha=1e-2, max_iter=3000))),
        ("hist_gb_poisson", "full", "reg", lambda: HistGradientBoostingRegressor(
            loss="poisson", max_depth=3, learning_rate=0.05, max_iter=300, random_state=rs)),
    ]


def _parse_target(t):
    kind, h = t.split("_")[1], int(t.split("_h")[1])
    return kind, h


def reg_alarm(cfg, d, pred, tkind, h):
    """Turn a count forecast into (score, alarm) under the same rule that defines the target."""
    tc = cfg["targets"]
    if tkind == "thr":
        k = tc["threshold"]["k"]
        score = (pred - d.thr_mu.values) / d.thr_sd.replace(0, np.nan).values
        return score, (score > k).astype(int)
    pct, mn = tc["growth"]["pct"], tc["growth"]["min_cases"]
    p = pct[h] if isinstance(pct, dict) else pct
    score = pred / (d.cases.values + 1)
    return score, ((pred >= (1 + p) * d.cases.values) & (pred >= mn)).astype(int)


def metrics(y, score, alarm, prob=None):
    out = {"n": len(y), "prevalence": y.mean()}
    two = len(np.unique(y)) > 1
    out["roc_auc"] = roc_auc_score(y, score) if two else np.nan
    out["pr_auc"] = average_precision_score(y, score) if two else np.nan
    out["brier"] = brier_score_loss(y, prob) if prob is not None else np.nan
    out["precision"] = precision_score(y, alarm, zero_division=0)
    out["recall"] = recall_score(y, alarm, zero_division=0)
    out["f1"] = f1_score(y, alarm, zero_division=0)
    neg = y == 0
    out["false_alarm_rate"] = alarm[neg].mean() if neg.any() else np.nan
    return out


def run(cfg):
    proc, out = cfg["paths"]["processed"], cfg["paths"]["outputs"]
    mc = cfg["model"]
    d_all = pd.read_csv(proc / "model_table.csv", parse_dates=["week_start"])
    groups = feature_groups(d_all.columns)
    if not groups["weather"] or len(groups["weather"]) == len([c for c in groups["weather"] if c.startswith("woy_")]):
        print("no weather features -> skipping weather/full models")
    specs = [s for s in model_specs(mc["random_state"])
             if s[1] == "cases" or len(groups[s[1]]) > len(groups["cases"]) or s[1] == "weather"]
    thr_p = mc["decision_threshold"]

    pooled, folds, oof_all, reg_err = [], [], [], []
    for t in target_columns(d_all.columns):
        tkind, h = _parse_target(t)
        need = groups["full"] + [t, f"y_fut_h{h}", "thr_mu", "thr_sd"]
        d = d_all.dropna(subset=need).reset_index(drop=True)
        d["year"] = d.week_start.dt.year
        target_date = d.week_start + pd.Timedelta(weeks=h)
        test_years = [y for y in sorted(d.year.unique()) if y >= mc["first_test_year"]]
        print(f"\n== {t}: n={len(d)}, prevalence={d[t].mean():.3f}, test years={test_years}")

        for name, fset, kind, factory in specs:
            cols = groups[fset]
            if not cols:
                continue
            oof = []
            for Y in test_years:
                te = d.year == Y
                tr = target_date < d.loc[te, "week_start"].min()   # purge: no target overlap
                Xtr, Xte = d.loc[tr, cols], d.loc[te, cols]
                if kind == "clf":
                    ytr = d.loc[tr, t].astype(int)
                    if ytr.nunique() < 2:
                        continue
                    m = factory().fit(Xtr, ytr)
                    prob = m.predict_proba(Xte)[:, 1]
                    score, alarm = prob, (prob >= thr_p).astype(int)
                else:
                    m = factory().fit(Xtr, d.loc[tr, f"y_fut_h{h}"])
                    pred = np.clip(m.predict(Xte), 0, None)
                    prob = None
                    score, alarm = reg_alarm(cfg, d.loc[te], pred, tkind, h)
                    yt = d.loc[te, f"y_fut_h{h}"].values
                    reg_err.append({"target": t, "model": name, "year": Y,
                                    "mae": np.mean(np.abs(pred - yt)),
                                    "rmse": np.sqrt(np.mean((pred - yt) ** 2))})
                ytest = d.loc[te, t].astype(int).values
                score = np.nan_to_num(score, nan=0.0)
                folds.append({"target": t, "model": name, "features": fset, "year": Y,
                              **metrics(ytest, score, alarm, prob)})
                oof.append(pd.DataFrame({"week_start": d.loc[te, "week_start"].values, "target": t,
                                         "model": f"{name}[{fset}]", "y": ytest, "score": score,
                                         "alarm": alarm}))
            if not oof:
                continue
            o = pd.concat(oof)
            oof_all.append(o)
            prob = o.score.values if kind == "clf" else None
            pooled.append({"target": t, "model": name, "features": fset, "kind": kind,
                           **metrics(o.y.values, o.score.values, o.alarm.values, prob)})

    tab = out / "tables"
    pooled = pd.DataFrame(pooled).sort_values(["target", "pr_auc"], ascending=[True, False])
    pooled.round(3).to_csv(tab / "model_cv_pooled.csv", index=False)
    pd.DataFrame(folds).round(3).to_csv(tab / "model_cv_by_fold.csv", index=False)
    oof_all = pd.concat(oof_all)
    oof_all.to_csv(proc / "oof_predictions.csv", index=False)
    if reg_err:
        re = pd.DataFrame(reg_err)
        re.round(2).to_csv(tab / "regression_errors_by_fold.csv", index=False)

    _interpret(cfg, d_all, groups, tab)
    _plot_best(pooled, oof_all, d_all, out / "figures")

    lines = ["# Model summary", "",
             "Rolling-origin CV: each test year uses all earlier weeks for training "
             f"(purged by h weeks). Alarm threshold for classifiers p>={thr_p}.", ""]
    show = ["model", "features", "roc_auc", "pr_auc", "brier", "precision", "recall", "f1",
            "false_alarm_rate", "prevalence", "n"]
    for t, g in pooled.groupby("target"):
        lines += [f"## {t}", "```", g[show].round(3).to_string(index=False), "```", ""]
    if reg_err:
        lines += ["## count regression error (mean over folds)", "```",
                  re.groupby(["target", "model"])[["mae", "rmse"]].mean().round(1).to_string(), "```"]
    lines.append("\nsee tables/feature_importance.csv, tables/tree_rules.txt, figures/model_best_*.png")
    for l in lines:
        print(l)
    write_summary(cfg, "model", lines)


def _interpret(cfg, d_all, groups, tab):
    rows, rules = [], []
    rs = cfg["model"]["random_state"]
    cols = groups["full"]
    for t in target_columns(d_all.columns):
        d = d_all.dropna(subset=cols + [t])
        X, y = d[cols], d[t].astype(int)
        if y.nunique() < 2:
            continue
        l1 = make_pipeline(StandardScaler(), LogisticRegression(penalty="l1", solver="liblinear",
                                                                C=0.1, max_iter=5000)).fit(X, y)
        rf = RandomForestClassifier(n_estimators=500, min_samples_leaf=5, n_jobs=-1, random_state=rs).fit(X, y)
        for c, b, imp in zip(cols, l1[-1].coef_[0], rf.feature_importances_):
            rows.append({"target": t, "feature": c, "logit_l1_coef_std": b, "rf_importance": imp})
        tree = DecisionTreeClassifier(max_depth=3, min_samples_leaf=20, random_state=rs).fit(X, y)
        rules += [f"===== {t} =====", export_text(tree, feature_names=cols), ""]
    fi = pd.DataFrame(rows)
    fi["abs_coef"] = fi.logit_l1_coef_std.abs()
    fi.sort_values(["target", "rf_importance"], ascending=[True, False]).round(4).to_csv(
        tab / "feature_importance.csv", index=False)
    (tab / "tree_rules.txt").write_text("\n".join(rules), encoding="utf-8")


def _plot_best(pooled, oof, d_all, fig_dir):
    for t, g in pooled[pooled.kind == "clf"].groupby("target"):
        best = g.sort_values("pr_auc", ascending=False).iloc[0]
        key = f"{best.model}[{best.features}]"
        o = oof[(oof.target == t) & (oof.model == key)]
        fig, ax1 = plt.subplots(figsize=(12, 4))
        seg = d_all[d_all.week_start.between(o.week_start.min(), o.week_start.max())]
        ax1.plot(seg.week_start, seg.cases, color="k", lw=1, label="cases")
        ax2 = ax1.twinx()
        ax2.plot(o.week_start, o.score, color="C0", lw=1, label=f"P(surge) {key}")
        ax2.scatter(o.week_start[o.y == 1], np.ones((o.y == 1).sum()) * 1.02, s=6, color="C3",
                    label="actual surge")
        ax2.set_ylim(0, 1.05)
        fig.legend(loc="upper left", fontsize=8)
        ax1.set_title(f"{t}: best by PR-AUC = {key} (out-of-sample)")
        fig.tight_layout(); fig.savefig(fig_dir / f"model_best_{t}.png", dpi=130); plt.close(fig)
