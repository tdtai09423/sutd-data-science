"""Stage `peak` (exploratory extension): once a wave is under way, will it turn down?

The main targets only ask whether cases will go UP. Here we ask the complementary question:
for a week t inside an epidemic wave, will counts have clearly fallen h weeks later?

  in-wave(t)  y[t] > mean of the past 52 weeks (thr_mu) and y[t] >= in_wave_min_cases
  decl_h      y[t+h] <= (1 - q[h]) * y[t]           (evaluated only on in-wave weeks)

Extra predictors motivated by SIR-type dynamics (all known at week t):
  accel_1 / accel_2   change in the weekly / 2-weekly log growth rate (a wave slows before it peaks)
  cum26 / cum52       log cases in the past 26 / 52 weeks (proxy for depletion of susceptibles)
  wave_len, wave_cum  weeks and log cases since the current wave started
  rel_max52           log distance to the 52-week maximum (0 = new high)
  lvl_mu              log distance to the 52-week mean

Same validation design as `model`: expanding-window rolling origin by week from
first_test_year, refit at every origin, training rows purged by horizon, target weeks in
holdout_from reported separately. Models are trained on all weeks (more data at early origins)
with an in-wave flag as a predictor, and scored on in-wave weeks only.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.calibration import calibration_curve
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .config import write_summary
from .features import feature_groups
from .modeling import LassoLogitCV, SeasonalRate, block_bootstrap, metrics

NEW = ["inw", "accel_1", "accel_2", "growth_2", "cum26", "cum52", "wave_len", "wave_cum",
       "rel_max52", "lvl_mu"]
REF = "momentum[trend]"
BASE = ["prior[woy]", "seasonal[woy]", REF]
NICE = {"prior[woy]": "prior (base rate)", "seasonal[woy]": "seasonal baseline",
        REF: "momentum baseline (growth_1)", "logit[cases]": "logistic, cases",
        "logit[peak]": "logistic, cases+peak", "lasso_logit[peak+weather]": "lasso, peak+weather",
        "random_forest[peak]": "random forest, peak", "ridge_logcount[cases]": "ridge log-count, cases",
        "ridge_logcount[peak]": "ridge log-count, peak"}


def add_peak_features(d, cfg):
    pc = cfg["peak"]
    d = d.copy()
    y = d.cases.astype(float)
    logy = np.log1p(y)
    d["growth_2"] = logy - logy.shift(2)
    d["accel_1"] = d.growth_1 - d.growth_1.shift(1)
    d["accel_2"] = d.growth_2 - d.growth_2.shift(2)
    d["cum26"] = np.log1p(y.rolling(26).sum())
    d["cum52"] = np.log1p(y.rolling(52).sum())
    above = (y > d.thr_mu).fillna(False)
    run_id = (~above).cumsum()
    d["wave_len"] = above.groupby(run_id).cumsum().astype(float)
    d["wave_cum"] = np.log1p((y * above).groupby(run_id).cumsum())
    d["rel_max52"] = logy - np.log1p(y.rolling(52).max())
    d["lvl_mu"] = logy - np.log1p(d.thr_mu)
    d["inw"] = (above & (y >= pc["in_wave_min_cases"])).astype(float).where(d.thr_mu.notna())
    for h in cfg["targets"]["horizons"]:
        q = pc["decline"][h]
        d[f"fthr_decl_h{h}"] = (1 - q) * y
        d[f"decl_h{h}"] = (d[f"y_fut_h{h}"] <= d[f"fthr_decl_h{h}"]).astype(float).where(
            d[f"y_fut_h{h}"].notna())
    return d


def specs(groups, rs):
    logit = lambda: make_pipeline(StandardScaler(), LogisticRegression(C=0.3, max_iter=5000))
    peak = groups["cases"] + NEW
    return [
        ("prior", "woy", ["woy"], "clf", lambda: DummyClassifier(strategy="prior")),
        ("seasonal", "woy", ["woy"], "clf", lambda: SeasonalRate()),
        ("momentum", "trend", ["growth_1"], "clf", logit),
        ("logit", "cases", groups["cases"] + ["inw"], "clf", logit),
        ("logit", "peak", peak, "clf", logit),
        ("lasso_logit", "peak+weather", peak + [c for c in groups["weather"] if c not in peak], "clf",
         lambda: LassoLogitCV()),
        ("random_forest", "peak", peak, "clf", lambda: RandomForestClassifier(
            n_estimators=300, min_samples_leaf=5, max_features="sqrt", n_jobs=-1, random_state=rs)),
        ("ridge_logcount", "cases", groups["cases"], "reg", lambda: make_pipeline(StandardScaler(), Ridge(10.0))),
        ("ridge_logcount", "peak", peak, "reg", lambda: make_pipeline(StandardScaler(), Ridge(10.0))),
    ]


def rolling(cfg, d_all, log=print):
    mc = cfg["model"]
    groups = feature_groups(d_all.columns)
    sp = specs(groups, mc["random_state"])
    allcols = sorted({c for s in sp for c in s[2]})
    out = []
    for h in cfg["targets"]["horizons"]:
        t = f"decl_h{h}"
        d = d_all.dropna(subset=allcols + [t, "inw"]).reset_index(drop=True)
        tdate = d.week_start + pd.Timedelta(weeks=h)
        test = d.index[(d.week_start.dt.year >= mc["first_test_year"]) & (d.inw == 1)]
        log(f"== {t}: train pool {len(d)}, in-wave test weeks {len(test)}, "
            f"declines {int(d.loc[test, t].sum())}")
        for name, fset, cols, kind, make in sp:
            rows = []
            for i in test:
                o = d.week_start[i]
                tr = tdate < o
                Xtr, Xte = d.loc[tr, cols], d.loc[[i], cols]
                if kind == "clf":
                    ytr = d.loc[tr, t].astype(int)
                    p = make().fit(Xtr, ytr).predict_proba(Xte)[0, 1] if ytr.nunique() > 1 else ytr.mean()
                    pc = np.nan
                else:
                    m = make().fit(Xtr, np.log1p(d.loc[tr, f"y_fut_h{h}"]))
                    sd = max(np.std(np.log1p(d.loc[tr, f"y_fut_h{h}"]) - m.predict(Xtr), ddof=1), 1e-3)
                    lte = m.predict(Xte)[0]
                    p = norm.cdf((np.log1p(d.loc[i, f"fthr_decl_h{h}"]) - lte) / sd)
                    pc = np.expm1(lte)
                rows.append({"week_start": o, "target": t, "model": f"{name}[{fset}]",
                             "y": int(d.loc[i, t]), "prob": p, "pred_count": pc,
                             "y_now": d.cases[i], "y_count": d.loc[i, f"y_fut_h{h}"]})
            out += rows
    oof = pd.DataFrame(out)
    h = oof.target.str.extract(r"_h(\d+)$")[0].astype(int)
    oof["target_week"] = oof.week_start + pd.to_timedelta(h, unit="W")
    hold = mc.get("holdout_from")
    oof["period"] = np.where(oof.target_week.dt.year >= hold, "holdout", "development")
    return oof


def waves(d, cfg):
    """Contiguous runs with y > 52-week mean; keep long, large ones. Peak = max week."""
    pc = cfg["peak"]
    above = (d.cases > d.thr_mu).values
    res, i = [], 0
    while i < len(d):
        if above[i]:
            j = i
            while j < len(d) and above[j]:
                j += 1
            k = i + int(np.argmax(d.cases.values[i:j]))
            if j - i >= pc["wave_min_weeks"] and d.cases[k] >= pc["wave_min_peak"]:
                res.append({"start": d.week_start[i], "end": d.week_start[j - 1],
                            "peak": d.week_start[k], "peak_cases": int(d.cases[k]), "weeks": j - i,
                            "peak_log1p": float(np.log1p(d.cases[k])),
                            "cum52_at_peak": float(d.cum52[k]) if pd.notna(d.cum52[k]) else np.nan})
            i = j
        else:
            i += 1
    return pd.DataFrame(res)


def peak_timing(oof, wv, models, thr, first_test):
    rows = []
    for _, w in wv[wv.peak >= pd.Timestamp(f"{first_test}-03-01")].iterrows():
        for (t, m), g in oof[oof.model.isin(models)].groupby(["target", "model"]):
            g = g[g.week_start.between(w.start, w.end)].sort_values("week_start")
            if g.empty:
                continue
            sig = g[g.prob >= thr]
            first = sig.week_start.min() if len(sig) else pd.NaT
            rows.append({"wave_peak": w.peak.date(), "target": t, "model": m,
                         "first_signal": first.date() if pd.notna(first) else None,
                         "first_signal_minus_peak_wk": (first - w.peak).days / 7 if pd.notna(first) else np.nan,
                         "signals_before_peak": int((sig.week_start < w.peak).sum()),
                         "false_signals_before_peak": int(((sig.week_start < w.peak) & (sig.y == 0)).sum()),
                         "weeks_before_peak_scored": int((g.week_start < w.peak).sum())})
    return pd.DataFrame(rows)


def run(cfg, reuse_oof=False):
    proc, out = cfg["paths"]["processed"], cfg["paths"]["outputs"]
    tab, fig = out / "tables", out / "figures"
    pc, mc = cfg["peak"], cfg["model"]
    d = add_peak_features(pd.read_csv(proc / "model_table.csv", parse_dates=["week_start"]), cfg)
    if reuse_oof:
        oof = pd.read_csv(proc / "peak_oof_predictions.csv", parse_dates=["week_start", "target_week"])
    else:
        oof = rolling(cfg, d)
        oof.to_csv(proc / "peak_oof_predictions.csv", index=False)

    parts = []
    for per in ["development", "holdout"]:
        g = oof[oof.period == per]
        rows = [{"target": t, "model": m, **metrics(x.y.values, x.prob.values, pc["alarm_prob"])}
                for (t, m), x in g.groupby(["target", "model"])]
        bs = block_bootstrap(g, ref=REF, B=pc["bootstrap"], block=pc["block"])
        parts.append(pd.DataFrame(rows).merge(bs, on=["target", "model"], how="left").assign(period=per))
    pooled = pd.concat(parts, ignore_index=True).sort_values(["period", "target", "pr_auc"],
                                                             ascending=[True, True, False])
    pooled.round(3).to_csv(tab / "peak_pooled.csv", index=False)
    dev = pooled[pooled.period == "development"]
    best = {t: g[~g.model.isin(BASE)].iloc[0].model for t, g in dev.groupby("target")}

    wv = waves(d, cfg)
    wv.to_csv(tab / "peak_waves.csv", index=False)
    timing = peak_timing(oof, wv, sorted(set(best.values())) + [REF], pc["alarm_prob"], mc["first_test_year"])
    timing = timing[[r.model in (best[r.target], REF) for r in timing.itertuples()]]
    timing.to_csv(tab / "peak_timing.csv", index=False)

    coefs = _coefs(cfg, d)
    coefs.round(4).to_csv(tab / "peak_coefficients.csv", index=False)
    _plots(cfg, d, oof, pooled, best, wv, timing, coefs, fig)

    show = ["model", "pr_auc", "pr_auc_lo", "pr_auc_hi", "p_better_than_persistence", "roc_auc", "brier",
            "precision", "recall", "positives", "n"]
    lines = ["# Peak / decline extension", "",
             f"In-wave: y[t] > 52-week mean and y[t] >= {pc['in_wave_min_cases']}. decl_h: "
             f"y[t+h] <= (1-q)*y[t], q = {pc['decline']}. Scored on in-wave weeks only.",
             f"Rolling origin by week from {mc['first_test_year']}, refit every origin, purged by horizon.",
             f"p_better = share of {pc['bootstrap']} block-bootstrap draws ({pc['block']}-week blocks) "
             f"beating the momentum baseline. Precision/recall at P >= {pc['alarm_prob']}.", ""]
    for per in ["development", "holdout"]:
        lines += [f"# {per}", ""]
        for t, g in pooled[pooled.period == per].groupby("target"):
            lines += [f"## {t} (best on development: {best[t]})", "```",
                      g[show].round(3).to_string(index=False), "```", ""]
    lines += ["## waves (y > 52-week mean, >= %d weeks, peak >= %d)" % (pc["wave_min_weeks"], pc["wave_min_peak"]),
              "```", wv.round(2).to_string(index=False), "```", "",
              f"## peak timing (first in-wave week with P >= {pc['alarm_prob']})", "```",
              timing.to_string(index=False), "```"]
    for l in lines:
        print(l)
    write_summary(cfg, "peak", lines)


def _coefs(cfg, d):
    """Standardised logistic coefficients (cases+peak features), development weeks only."""
    groups = feature_groups(d.columns)
    cols = groups["cases"] + NEW
    hold = pd.Timestamp(f"{cfg['model']['holdout_from']}-01-01")
    rows = []
    for h in cfg["targets"]["horizons"]:
        t = f"decl_h{h}"
        x = d.dropna(subset=cols + [t])
        x = x[x.week_start + pd.Timedelta(weeks=h) < hold]
        m = make_pipeline(StandardScaler(), LogisticRegression(C=0.3, max_iter=5000)).fit(x[cols], x[t].astype(int))
        rows += [{"target": t, "feature": c, "coef_std": b} for c, b in zip(cols, m[-1].coef_[0])]
    return pd.DataFrame(rows)


def _plots(cfg, d, oof, pooled, best, wv, timing, coefs, fig_dir):
    plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False})
    H = cfg["targets"]["horizons"]
    ft = cfg["model"]["first_test_year"]
    hold = cfg["model"]["holdout_from"]
    nice = lambda m: NICE.get(m, m)

    # 1 phase portrait: growth vs level; peaks happen at very different levels ---------------
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw={"width_ratios": [1.6, 1]})
    g4 = (np.log1p(d.cases) - np.log1p(d.cases).shift(4)) / 4
    for k, w in wv.iterrows():
        s = d.week_start.between(w.start - pd.Timedelta(weeks=8), w.end)
        ax[0].plot(np.log1p(d.cases[s]), g4[s], lw=1.2, color=f"C{k}", alpha=.85,
                   label=f"wave peaking {w.peak:%Y-%m}")
        pk = d.week_start == w.peak
        ax[0].scatter(np.log1p(d.cases[pk]), g4[pk], color=f"C{k}", s=60, edgecolor="k", zorder=3)
    ax[0].axhline(0, color="0.4", lw=.8, ls=":")
    ax[0].set_xlabel("log(1 + weekly DF cases)")
    ax[0].set_ylabel("average weekly log growth, past 4 weeks")
    ax[0].set_title("Phase portrait of each wave (dot = peak week)", fontsize=10)
    ax[0].legend(fontsize=7, frameon=False, loc="lower left")
    ax[1].barh([f"{p:%Y-%m}" for p in wv.peak], wv.peak_log1p, color=[f"C{k}" for k in range(len(wv))])
    for k, w in wv.iterrows():
        ax[1].text(w.peak_log1p + .05, k, f"{w.peak_cases} cases", va="center", fontsize=8)
    ax[1].set_xlim(0, 8.8)
    ax[1].set_xlabel("log(1 + cases) at the peak")
    ax[1].set_title("Peak level differs by wave: no fixed ceiling", fontsize=10)
    fig.tight_layout(); fig.savefig(fig_dir / "peak_01_phase_portrait.png"); plt.close(fig)

    # 2 target definition -------------------------------------------------------------------
    h0 = 2 if 2 in H else H[0]
    s = d[d.week_start.dt.year >= ft]
    fig, ax = plt.subplots(figsize=(12, 3.8))
    ax.plot(s.week_start, s.cases, color="k", lw=1, label="DF cases")
    ax.plot(s.week_start, s.thr_mu, color="C0", lw=.8, label="52-week mean")
    ax.fill_between(s.week_start, 0, s.cases.max() * 1.05, where=s.inw == 1, color="C1", alpha=.15,
                    step="mid", label="in-wave weeks (scored)")
    lab = (s.inw == 1) & (s[f"decl_h{h0}"] == 1)
    ax.scatter(s.week_start[lab], s.cases[lab], s=10, color="C3", zorder=3,
               label=f"decl_h{h0}=1: cases down >= {int(100 * cfg['peak']['decline'][h0])}% in {h0} weeks")
    for _, w in wv[wv.peak.dt.year >= ft].iterrows():
        ax.axvline(w.peak, color="C3", lw=.8, ls="--")
    ax.legend(fontsize=8, frameon=False, loc="upper left")
    ax.set_title("Decline target on in-wave weeks (dashed = wave peak)", fontsize=10)
    fig.tight_layout(); fig.savefig(fig_dir / "peak_02_target_definition.png"); plt.close(fig)

    # 3 PR-AUC with CI by horizon ------------------------------------------------------------
    dev = pooled[pooled.period == "development"]
    order = [m for m in NICE if m in set(dev.model)]
    fig, ax = plt.subplots(1, len(H), figsize=(4.4 * len(H), 4.2), sharey=True)
    for a, h in zip(np.atleast_1d(ax), H):
        g = dev[dev.target == f"decl_h{h}"].set_index("model").reindex(order)
        yy = np.arange(len(order))
        col = ["0.6" if m in BASE else ("C3" if m == best[f"decl_h{h}"] else "C0") for m in order]
        a.errorbar(g.pr_auc, yy, xerr=[g.pr_auc - g.pr_auc_lo, g.pr_auc_hi - g.pr_auc], fmt="none",
                   ecolor="0.7", lw=1)
        a.scatter(g.pr_auc, yy, c=col, zorder=3)
        a.axvline(g.prevalence.iloc[0], color="0.5", ls=":", lw=1)
        a.axvline(g.loc[REF, "pr_auc"], color="C3", ls="--", lw=.8)
        a.set_yticks(yy, [nice(m) for m in order], fontsize=8)
        a.set_title(f"decline in {h} wk (n={int(g.n.iloc[0])}, pos={int(g.positives.iloc[0])})", fontsize=10)
        a.set_xlim(0, 1); a.set_xlabel("PR-AUC (development)")
    np.atleast_1d(ax)[0].invert_yaxis()
    fig.tight_layout(); fig.savefig(fig_dir / "peak_03_pr_auc.png"); plt.close(fig)

    # 4 timelines per test wave ---------------------------------------------------------------
    tw = wv[wv.peak >= pd.Timestamp(f"{ft}-03-01")].reset_index(drop=True)
    t = f"decl_h{h0}"
    fig, ax = plt.subplots(1, len(tw), figsize=(4.2 * len(tw), 3.8), squeeze=False)
    for a, (_, w) in zip(ax[0], tw.iterrows()):
        seg = d[d.week_start.between(w.start - pd.Timedelta(weeks=6), w.end + pd.Timedelta(weeks=6))]
        a.plot(seg.week_start, seg.cases, color="k", lw=1)
        a.axvline(w.peak, color="C3", ls="--", lw=.8)
        a2 = a.twinx()
        for m, c in [(best[t], "C0"), (REF, "0.5")]:
            o = oof[(oof.target == t) & (oof.model == m) & oof.week_start.between(seg.week_start.min(), seg.week_start.max())]
            a2.plot(o.week_start, o.prob, color=c, marker=".", lw=1, label=nice(m))
        a2.axhline(cfg["peak"]["alarm_prob"], color="C1", ls=":", lw=.8)
        a2.set_ylim(0, 1.02)
        a.set_title(f"wave peaking {w.peak:%Y-%m-%d} ({w.peak_cases})", fontsize=9)
        a.tick_params(axis="x", labelsize=7, rotation=30)
    ax[0][0].set_ylabel("DF cases")
    a2.set_ylabel(f"P(decline in {h0} weeks)")
    a2.legend(fontsize=7, frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(fig_dir / "peak_04_timelines.png"); plt.close(fig)

    # 5 probability aligned on the peak week (no alarm threshold needed) ---------------------
    fig, ax = plt.subplots(1, len(H), figsize=(4.4 * len(H), 3.8), sharey=True, squeeze=False)
    for a, h in zip(ax[0], H):
        tt = f"decl_h{h}"
        for k, w in tw.iterrows():
            for m, ls in [(best[tt], "-"), (REF, ":")]:
                o = oof[(oof.target == tt) & (oof.model == m) & oof.week_start.between(w.start, w.end)]
                rel = (o.week_start - w.peak).dt.days / 7
                keep = rel.between(-16, 10)
                a.plot(rel[keep], o.prob[keep], ls=ls, color=f"C{k}", lw=1.2 if ls == "-" else .8,
                       label=f"{w.peak:%Y-%m}" if ls == "-" else None)
        a.axvline(0, color="C3", ls="--", lw=.8)
        a.axvline(-h, color="0.6", ls="--", lw=.6)
        a.set_title(f"decline in {h} wk: {nice(best[tt])} (solid), momentum (dotted)", fontsize=8)
        a.set_xlabel("weeks from wave peak (grey: origin = peak - h)")
        a.set_ylim(0, 1)
    ax[0][0].set_ylabel("P(clear decline h weeks later)")
    ax[0][0].legend(title="wave peak", fontsize=7, frameon=False)
    fig.tight_layout(); fig.savefig(fig_dir / "peak_05_peak_aligned.png"); plt.close(fig)

    # 6 coefficients ---------------------------------------------------------------------------
    c = coefs[coefs.target == t].copy()
    c = c.reindex(c.coef_std.abs().sort_values(ascending=False).index).head(14)[::-1]
    fig, ax = plt.subplots(figsize=(7, 4.6))
    ax.barh(c.feature, c.coef_std, color=["C3" if f in NEW else "C0" for f in c.feature])
    ax.axvline(0, color="0.4", lw=.8)
    ax.set_xlabel("standardised logistic coefficient (> 0: decline more likely)")
    ax.set_title(f"{t}: top predictors, development fit (red = new peak features)", fontsize=10)
    fig.tight_layout(); fig.savefig(fig_dir / "peak_06_coefficients.png"); plt.close(fig)

    # 7 calibration + 2022 --------------------------------------------------------------------
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.2))
    od = oof[(oof.period == "development") & (oof.target == t)]
    for m, col in [(best[t], "C0"), (REF, "0.5"), ("seasonal[woy]", "C2")]:
        o = od[od.model == m]
        fy, fx = calibration_curve(o.y, o.prob, n_bins=6, strategy="quantile")
        ax[0].plot(fx, fy, marker="o", color=col, label=nice(m))
    ax[0].plot([0, 1], [0, 1], color="0.5", ls=":")
    ax[0].set_xlabel("predicted P(decline)"); ax[0].set_ylabel("observed frequency")
    ax[0].set_title(f"Calibration, {t}, development", fontsize=10); ax[0].legend(fontsize=7, frameon=False)
    p = pooled[pooled.model.isin([best[x] for x in best] + [REF, "prior[woy]"])]
    lab = []
    for k, h in enumerate(H):
        tt = f"decl_h{h}"
        for j, (m, col) in enumerate([("prior[woy]", "0.8"), (REF, "0.5"), (best[tt], "C0")]):
            for per, hatch in [("development", None), ("holdout", "//")]:
                v = p[(p.target == tt) & (p.model == m) & (p.period == per)].pr_auc
                x = k * 7 + j * 2 + (per == "holdout") * .9
                ax[1].bar(x, v.iloc[0] if len(v) else np.nan, width=.85, color=col, hatch=hatch,
                          edgecolor="k", lw=.3)
        lab.append((k * 7 + 2.5, f"h={h}\nbest: {nice(best[tt])}"))
    ax[1].set_xticks([x for x, _ in lab], [s for _, s in lab], fontsize=7)
    ax[1].set_ylim(0, 1); ax[1].set_ylabel("PR-AUC")
    ax[1].set_title(f"Development (plain) vs {hold} (hatched): prior / momentum / best", fontsize=9)
    fig.tight_layout(); fig.savefig(fig_dir / "peak_07_calibration_holdout.png"); plt.close(fig)
