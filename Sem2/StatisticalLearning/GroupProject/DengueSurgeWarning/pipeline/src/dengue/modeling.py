"""Stage `model`: rolling-origin evaluation by week, comparing classifiers, count regressions and
seasonal / persistence baselines for each surge target.

Evaluation design
- Expanding window: at each forecast origin (every `refit_every` weeks from `first_test_year`)
  every model is refitted on all rows whose target week is strictly before that origin
  (purge: no label that would still be unknown at forecast time), then forecasts the next
  `refit_every` weeks. Predictors only use information available at week t (see features.py).
- Every model outputs P(surge). Count regressions become probabilities of crossing the
  target's threshold via a log-normal predictive distribution fitted on training residuals.
- Alarm: P(surge) >= c with c = 1 / (1 + cost_ratio), cost_ratio = cost(miss) / cost(false alarm).
- Uncertainty: moving-block bootstrap of the out-of-sample predictions.
"""
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.calibration import calibration_curve
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, PoissonRegressor, Ridge
from sklearn.metrics import (average_precision_score, brier_score_loss, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text

from .config import write_summary
from .features import build_table, feature_groups, parse_target, target_columns

warnings.filterwarnings("ignore")

PERSIST_FEATURE = {"thr": "marg_thr", "seas": "marg_seas", "grow": "growth_1"}
BASELINES = ["prior", "seasonal", "persistence"]


class SeasonalRate(BaseEstimator, ClassifierMixin):
    """Seasonal baseline: historical surge rate in the same weeks of the year (+-halfwidth),
    shrunk towards the overall rate. X must contain one column: week of year."""

    def __init__(self, halfwidth=2, strength=5.0):
        self.halfwidth, self.strength = halfwidth, strength

    def fit(self, X, y):
        w, y = np.asarray(X).ravel().astype(int), np.asarray(y)
        self.classes_ = np.array([0, 1])
        self.base_ = y.mean()
        self.rate_ = {}
        for k in range(1, 54):
            dist = np.abs(w - k)
            m = np.minimum(dist, 53 - dist) <= self.halfwidth
            self.rate_[k] = (y[m].sum() + self.strength * self.base_) / (m.sum() + self.strength)
        return self

    def predict_proba(self, X):
        p = np.array([self.rate_.get(int(k), self.base_) for k in np.asarray(X).ravel()])
        return np.c_[1 - p, p]


class LassoLogitCV(BaseEstimator, ClassifierMixin):
    """L1 logistic regression with C chosen by forward-chaining CV on log-loss.
    Folds whose training part has a single class are skipped; if none is usable, C=0.1."""

    def __init__(self, Cs=tuple(np.logspace(-3, 1, 9)), n_splits=4):
        self.Cs, self.n_splits = Cs, n_splits

    def _fit_C(self, X, y, C):
        return make_pipeline(StandardScaler(), LogisticRegression(
            penalty="l1", solver="liblinear", C=C, max_iter=5000)).fit(X, y)

    def fit(self, X, y):
        from sklearn.metrics import log_loss
        X, y = np.asarray(X), np.asarray(y)
        loss = np.zeros(len(self.Cs))
        used = 0
        for tr, te in TimeSeriesSplit(self.n_splits).split(X):
            if len(np.unique(y[tr])) < 2:
                continue
            used += 1
            for i, C in enumerate(self.Cs):
                p = self._fit_C(X[tr], y[tr], C).predict_proba(X[te])[:, 1]
                loss[i] += log_loss(y[te], p, labels=[0, 1])
        self.C_ = self.Cs[int(np.argmin(loss))] if used else 0.1
        self.model_ = self._fit_C(X, y, self.C_)
        self.classes_ = self.model_.classes_
        return self

    def predict_proba(self, X):
        return self.model_.predict_proba(np.asarray(X))


def model_specs(rs):
    """(name, feature_set, kind, factory). kind: clf -> probability, reg -> count forecast."""
    scaled_logit = lambda **kw: make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000, **kw))
    return [
        ("prior", "woy", "clf", lambda: DummyClassifier(strategy="prior")),
        ("seasonal", "woy", "clf", lambda: SeasonalRate()),
        ("persistence", "persist", "clf", lambda: scaled_logit(C=1.0)),
        ("logit", "cases", "clf", lambda: scaled_logit(C=1.0)),
        ("logit", "weather", "clf", lambda: scaled_logit(C=1.0)),
        ("logit", "full", "clf", lambda: scaled_logit(C=1.0)),
        ("lasso_logit", "full", "clf", lambda: LassoLogitCV()),
        ("cart_d3", "full", "clf", lambda: DecisionTreeClassifier(
            max_depth=3, min_samples_leaf=20, random_state=rs)),
        ("random_forest", "full", "clf", lambda: RandomForestClassifier(
            n_estimators=300, min_samples_leaf=5, max_features="sqrt", n_jobs=-1, random_state=rs)),
        ("poisson_glm", "full", "reg", lambda: make_pipeline(StandardScaler(), PoissonRegressor(
            alpha=1e-2, max_iter=3000))),
        ("ridge_logcount", "full", "reg", lambda: make_pipeline(StandardScaler(), Ridge(alpha=10.0))),
    ]


def _cols(groups, fset, base_kind):
    if fset == "woy":
        return ["woy"]
    if fset == "persist":
        return [PERSIST_FEATURE[base_kind]]
    return groups[fset]


def _reg_fit_predict(name, m, Xtr, ytr, Xte):
    """Fit a count model, return (point forecast on count scale, log-scale residual sd)."""
    if name == "ridge_logcount":
        m.fit(Xtr, np.log1p(ytr))
        ltr, lte = m.predict(Xtr), m.predict(Xte)
    else:
        m.fit(Xtr, ytr)
        ltr, lte = np.log1p(np.clip(m.predict(Xtr), 0, None)), np.log1p(np.clip(m.predict(Xte), 0, None))
    sd = np.std(np.log1p(ytr) - ltr, ddof=1)
    return lte, max(sd, 1e-3)


def metrics(y, prob, c):
    alarm = (prob >= c).astype(int)
    two = len(np.unique(y)) > 1
    neg = y == 0
    return {"n": len(y), "positives": int(y.sum()), "prevalence": y.mean(),
            "roc_auc": roc_auc_score(y, prob) if two else np.nan,
            "pr_auc": average_precision_score(y, prob) if two else np.nan,
            "brier": brier_score_loss(y, prob),
            "precision": precision_score(y, alarm, zero_division=0),
            "recall": recall_score(y, alarm, zero_division=0),
            "f1": f1_score(y, alarm, zero_division=0),
            "false_alarm_rate": alarm[neg].mean() if neg.any() else np.nan,
            "alarms_per_year": alarm.mean() * 52.18}


def rolling_origin(cfg, d_all, targets, specs, log=print):
    """Expanding-window, refit every `refit_every` weeks. Returns out-of-sample predictions."""
    mc = cfg["model"]
    step = mc["refit_every"]
    groups = feature_groups(d_all.columns)
    oof = []
    for t in targets:
        kind, base, h = parse_target(t)
        need = groups["full"] + [t, f"y_fut_h{h}", f"fthr_{base}_h{h}", "woy"]
        d = d_all.dropna(subset=need).reset_index(drop=True)
        tdate = d.week_start + pd.Timedelta(weeks=h)
        test_idx = np.flatnonzero(d.week_start.dt.year >= mc["first_test_year"])
        if len(test_idx) == 0:
            continue
        log(f"== {t}: n={len(d)}, test n={len(test_idx)}, test positives={int(d.loc[test_idx, t].sum())}")
        origins = d.week_start.iloc[test_idx].sort_values().unique()[::step]
        for name, fset, mkind, factory in specs:
            cols = _cols(groups, fset, base)
            parts = []
            for i, o in enumerate(origins):
                end = origins[i + 1] if i + 1 < len(origins) else pd.Timestamp.max
                te = (d.week_start >= o) & (d.week_start < end) & (d.week_start.dt.year >= mc["first_test_year"])
                tr = tdate < o
                if not te.any():
                    continue
                Xtr, Xte = d.loc[tr, cols], d.loc[te, cols]
                if mkind == "clf":
                    ytr = d.loc[tr, t].astype(int)
                    if ytr.nunique() < 2:
                        prob = np.full(te.sum(), ytr.mean())
                    else:
                        prob = factory().fit(Xtr, ytr).predict_proba(Xte)[:, 1]
                    pred = np.full(te.sum(), np.nan)
                else:
                    lte, sd = _reg_fit_predict(name, factory(), Xtr, d.loc[tr, f"y_fut_h{h}"], Xte)
                    lthr = np.log1p(d.loc[te, f"fthr_{base}_h{h}"].values)
                    # strict ">" thresholds: P(log1p(Y) > log1p(thr))
                    prob = 1 - norm.cdf((lthr - lte) / sd)
                    pred = np.expm1(lte)
                parts.append(pd.DataFrame({
                    "week_start": d.loc[te, "week_start"].values, "target": t,
                    "model": f"{name}[{fset}]", "y": d.loc[te, t].astype(int).values,
                    "prob": prob, "pred_count": pred, "y_count": d.loc[te, f"y_fut_h{h}"].values}))
            if parts:
                oof.append(pd.concat(parts))
    return pd.concat(oof, ignore_index=True)


def block_bootstrap(oof, ref="persistence[persist]", B=500, block=26, seed=0):
    """Moving-block bootstrap (blocks of consecutive test weeks) of PR-AUC and of the
    PR-AUC difference to the persistence baseline."""
    rng = np.random.default_rng(seed)
    rows = []
    for t, g in oof.groupby("target"):
        wide = g.pivot_table(index="week_start", columns="model", values="prob")
        y = g.drop_duplicates("week_start").set_index("week_start").y.reindex(wide.index).values
        n = len(y)
        nb = int(np.ceil(n / block))
        draws = {m: [] for m in wide.columns}
        diffs = {m: [] for m in wide.columns}
        for _ in range(B):
            starts = rng.integers(0, max(n - block, 1), nb)
            idx = np.concatenate([np.arange(s, min(s + block, n)) for s in starts])[:n]
            if y[idx].sum() == 0 or y[idx].sum() == len(idx):
                continue
            ref_ap = average_precision_score(y[idx], wide[ref].values[idx]) if ref in wide else np.nan
            for m in wide.columns:
                ap = average_precision_score(y[idx], wide[m].values[idx])
                draws[m].append(ap)
                diffs[m].append(ap - ref_ap)
        for m in wide.columns:
            if draws[m]:
                rows.append({"target": t, "model": m,
                             "pr_auc_lo": np.percentile(draws[m], 2.5),
                             "pr_auc_hi": np.percentile(draws[m], 97.5),
                             "diff_vs_persistence_lo": np.percentile(diffs[m], 2.5),
                             "diff_vs_persistence_hi": np.percentile(diffs[m], 97.5),
                             "p_better_than_persistence": np.mean(np.array(diffs[m]) > 0)})
    return pd.DataFrame(rows)


def pooled_table(oof, c):
    rows = []
    for (t, m), g in oof.groupby(["target", "model"]):
        rows.append({"target": t, "model": m, **metrics(g.y.values, g.prob.values, c)})
    return pd.DataFrame(rows).sort_values(["target", "pr_auc"], ascending=[True, False])


def run(cfg):
    proc, out = cfg["paths"]["processed"], cfg["paths"]["outputs"]
    tab, fig = out / "tables", out / "figures"
    mc = cfg["model"]
    d_all = pd.read_csv(proc / "model_table.csv", parse_dates=["week_start"])
    specs = model_specs(mc["random_state"])
    if mc.get("models"):
        specs = [s for s in specs if s[0] in mc["models"] or s[0] in BASELINES]
    targets = [t for t in target_columns(d_all.columns)
               if not mc.get("targets") or t in mc["targets"]]
    c = 1 / (1 + mc["cost_ratio"])

    oof = rolling_origin(cfg, d_all, targets, specs)
    oof.to_csv(proc / "oof_predictions.csv", index=False)
    pooled = pooled_table(oof, c)
    boot = block_bootstrap(oof, B=mc["bootstrap"])
    pooled = pooled.merge(boot, on=["target", "model"], how="left")
    pooled.round(3).to_csv(tab / "model_cv_pooled.csv", index=False)

    by_year = []
    for (t, m, y), g in oof.groupby(["target", "model", oof.week_start.dt.year]):
        by_year.append({"target": t, "model": m, "year": y, **metrics(g.y.values, g.prob.values, c)})
    pd.DataFrame(by_year).round(3).to_csv(tab / "model_cv_by_year.csv", index=False)

    cost_rows = []
    for (t, m), g in oof.groupby(["target", "model"]):
        for r in mc["cost_ratio_grid"]:
            cost_rows.append({"target": t, "model": m, "cost_ratio": r, "threshold": 1 / (1 + r),
                              **{k: v for k, v in metrics(g.y.values, g.prob.values, 1 / (1 + r)).items()
                                 if k in ["precision", "recall", "false_alarm_rate", "alarms_per_year"]}})
    pd.DataFrame(cost_rows).round(3).to_csv(tab / "alarm_cost_tradeoff.csv", index=False)

    reg = oof[oof.pred_count.notna()]
    reg_err = (reg.assign(ae=(reg.pred_count - reg.y_count).abs(),
                          se=(reg.pred_count - reg.y_count) ** 2)
               .groupby(["target", "model"]).agg(mae=("ae", "mean"), rmse=("se", lambda s: np.sqrt(s.mean()))))
    reg_err = reg_err[reg_err.index.get_level_values(0).str.contains("_thr_")]  # same counts for all kinds
    reg_err.round(1).to_csv(tab / "regression_errors.csv")

    sens = _delay_sensitivity(cfg, specs, c) if mc.get("delay_sensitivity") else None
    if sens is not None:
        sens.round(3).to_csv(tab / "delay_sensitivity.csv")
    _interpret(cfg, d_all, tab)
    _plot_calibration(oof, pooled, fig, cfg)
    _plot_best(pooled, oof, d_all, fig)

    lines = ["# Model summary", "",
             f"Rolling-origin by week: expanding window from {mc['first_test_year']}, refit every "
             f"{mc['refit_every']} week(s), training rows purged so every label is known at the origin.",
             f"Alarm if P(surge) >= {c:.2f} (cost of a missed surge = {mc['cost_ratio']} x a false alarm).",
             "CI: 95% moving-block bootstrap (26-week blocks). p_better = share of bootstrap draws where "
             "the model beats the persistence baseline on PR-AUC.", ""]
    show = ["model", "pr_auc", "pr_auc_lo", "pr_auc_hi", "p_better_than_persistence", "roc_auc", "brier",
            "precision", "recall", "alarms_per_year", "positives", "n"]
    for t, g in pooled.groupby("target", sort=False):
        lines += [f"## {t}", "```", g[show].round(3).to_string(index=False), "```", ""]
    lines += ["## count regression error (out-of-sample, cases)", "```", reg_err.round(1).to_string(), "```"]
    if sens is not None:
        lines += ["", "## reporting-delay sensitivity (PR-AUC; delay=1: week t counts unknown)", "```",
                  sens.round(3).to_string(), "```"]
    lines.append("\nsee tables/*.csv, tables/tree_rules.txt, figures/model_calibration.png, figures/model_best_*.png")
    for l in lines:
        print(l)
    write_summary(cfg, "model", lines)


def _delay_sensitivity(cfg, specs, c):
    """Re-run the main h=1 targets with week t's counts treated as unreported."""
    import copy
    cfg2 = copy.deepcopy(cfg)
    cfg2["features"]["report_delay"] = 1
    weekly = pd.read_csv(cfg["paths"]["processed"] / "weekly.csv", parse_dates=["week_start"])
    d1 = build_table(cfg2, weekly)
    keep = ["persistence", "seasonal", "logit", "lasso_logit", "poisson_glm"]
    sp = [s for s in specs if s[0] in keep]
    ts = cfg["model"]["delay_sensitivity_targets"]
    res = {}
    for delay, d in [(0, pd.read_csv(cfg["paths"]["processed"] / "model_table.csv", parse_dates=["week_start"])),
                     (1, d1)]:
        o = rolling_origin(cfg, d, ts, sp, log=lambda *_: None)
        res[f"delay{delay}"] = pooled_table(o, c).set_index(["target", "model"]).pr_auc
    return pd.DataFrame(res)


def _interpret(cfg, d_all, tab):
    """Full-sample fits for interpretation only (not for evaluation)."""
    rows, rules = [], []
    rs = cfg["model"]["random_state"]
    cols = feature_groups(d_all.columns)["full"]
    for t in [t for t in target_columns(d_all.columns) if "onset" not in t]:
        d = d_all.dropna(subset=cols + [t])
        X, y = d[cols], d[t].astype(int)
        l1 = LassoLogitCV().fit(X, y).model_
        rf = RandomForestClassifier(n_estimators=300, min_samples_leaf=5, n_jobs=-1, random_state=rs).fit(X, y)
        for col, b, imp in zip(cols, l1[-1].coef_[0], rf.feature_importances_):
            rows.append({"target": t, "feature": col, "lasso_coef_std": b, "rf_importance": imp,
                         "lasso_C": l1[-1].C})
        tree = DecisionTreeClassifier(max_depth=3, min_samples_leaf=20, random_state=rs).fit(X, y)
        rules += [f"===== {t} =====", export_text(tree, feature_names=cols), ""]
    fi = pd.DataFrame(rows)
    fi["abs_coef"] = fi.lasso_coef_std.abs()
    fi.sort_values(["target", "rf_importance"], ascending=[True, False]).round(4).to_csv(
        tab / "feature_importance.csv", index=False)
    (tab / "tree_rules.txt").write_text("\n".join(rules), encoding="utf-8")


def _plot_calibration(oof, pooled, fig_dir, cfg):
    ts = [t for t in cfg["model"]["delay_sensitivity_targets"] if t in set(oof.target)]
    if not ts:
        return
    fig, axes = plt.subplots(1, len(ts), figsize=(5 * len(ts), 4.5), squeeze=False)
    for a, t in zip(axes[0], ts):
        g = pooled[pooled.target == t]
        best = g[~g.model.str.split("[").str[0].isin(BASELINES)].iloc[0].model
        for m in [best, "persistence[persist]", "seasonal[woy]"]:
            o = oof[(oof.target == t) & (oof.model == m)]
            fy, fx = calibration_curve(o.y, o.prob, n_bins=8, strategy="quantile")
            a.plot(fx, fy, marker="o", label=m)
        a.plot([0, 1], [0, 1], color="0.5", ls=":")
        a.set_title(t, fontsize=10)
        a.set_xlabel("predicted P(surge)")
    axes[0][0].set_ylabel("observed frequency")
    axes[0][-1].legend(fontsize=8, frameon=False)
    fig.tight_layout(); fig.savefig(fig_dir / "model_calibration.png", dpi=130); plt.close(fig)


def _plot_best(pooled, oof, d_all, fig_dir):
    for f in fig_dir.glob("model_best_*.png"):
        f.unlink()
    for t, g in pooled.groupby("target"):
        if "_h1" not in t:
            continue
        key = g[~g.model.str.split("[").str[0].isin(BASELINES)].iloc[0].model
        o = oof[(oof.target == t) & (oof.model == key)]
        fig, ax1 = plt.subplots(figsize=(12, 4))
        seg = d_all[d_all.week_start.between(o.week_start.min(), o.week_start.max())]
        ax1.plot(seg.week_start, seg.cases, color="k", lw=1, label="dengue fever cases")
        ax2 = ax1.twinx()
        ax2.plot(o.week_start, o.prob, color="C0", lw=1, label=f"P(surge) {key}")
        ax2.scatter(o.week_start[o.y == 1], np.ones((o.y == 1).sum()) * 1.02, s=6, color="C3",
                    label="actual surge")
        ax2.set_ylim(0, 1.05)
        fig.legend(loc="upper left", fontsize=8)
        ax1.set_title(f"{t}: best non-baseline model by PR-AUC = {key} (out-of-sample)")
        fig.tight_layout(); fig.savefig(fig_dir / f"model_best_{t}.png", dpi=130); plt.close(fig)
