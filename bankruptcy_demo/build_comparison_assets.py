"""Build assets/model_comparison.json for the two comparison pages.

Reads the saved outputs of the notebooks (results/*.csv, data/processed/
preds.csv.gz, models/*.joblib) and writes one small JSON file. It never
writes to the notebook folder.

Run once (needs pandas, numpy, scikit-learn):
    python build_comparison_assets.py "path/to/ML Project"
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import (balanced_accuracy_score, precision_recall_curve,
                             roc_auc_score, roc_curve)

SRC = sys.argv[1] if len(sys.argv) > 1 else "ML Project"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets",
                   "model_comparison.json")
MODELS = ["altman_z", "logreg", "rf", "xgb", "ebm"]


def thin(x, y, n=120):
    """Keep about n points of a curve so the file stays small."""
    idx = np.unique(np.linspace(0, len(x) - 1, n).astype(int))
    return [[round(float(x[i]), 4), round(float(y[i]), 4)] for i in idx]


met = pd.read_csv(os.path.join(SRC, "results", "step4_metrics.csv"))
topk = pd.read_csv(os.path.join(SRC, "results", "step4b_recall_topk.csv"))
pair = pd.read_csv(os.path.join(SRC, "results", "step6_pairwise_models.csv"))
vsalt = pd.read_csv(os.path.join(SRC, "results", "step4_paired_vs_altman.csv"))
preds = pd.read_csv(os.path.join(SRC, "data", "processed", "preds.csv.gz"))

out = {"metrics": [], "pairwise_full": [], "vs_altman": [], "curves": {},
       "size_mb": {}, "balanced_acc": {}}

test = met[met.split == "test"]
for r in test.itertuples():
    k = topk[(topk.model == r.model) & (topk.features == r.features)
             & (topk.horizon == r.horizon)].iloc[0]
    out["metrics"].append({
        "model": r.model, "features": r.features, "h": int(r.horizon),
        "pos": int(r.positives), "n": int(r.n),
        "roc": r.ROC_AUC, "roc_lo": r.ROC_AUC_lo, "roc_hi": r.ROC_AUC_hi,
        "pr": r.PR_AUC, "pr_lo": r.PR_AUC_lo, "pr_hi": r.PR_AUC_hi,
        "lift": r.PR_lift, "f2": r.F2, "brier_skill": r.Brier_skill,
        "rec5": float(k["recall@top5%"]), "rec10": float(k["recall@top10%"])})

for r in pair.itertuples():
    out["pairwise_full"].append({
        "h": int(r.horizon), "a": r.model_a, "b": r.model_b,
        "metric": r.metric, "delta": r.delta_a_minus_b, "lo": r.lo,
        "hi": r.hi, "sig": bool(r.excludes_zero)})

for r in vsalt.itertuples():
    out["vs_altman"].append({
        "model": r.model, "features": r.features, "h": int(r.horizon),
        "metric": r.metric, "delta": r.delta_mean, "lo": r.ci_lo,
        "hi": r.ci_hi})

# curves on the test years, static features
for h in (1, 2, 3):
    for m in MODELS:
        f = "-" if m == "altman_z" else "static"
        d = preds[(preds.split == "test") & (preds.horizon == h)
                  & (preds.model == m) & (preds.features == f)]
        fpr, tpr, _ = roc_curve(d.y, d.score)
        pr, rc, _ = precision_recall_curve(d.y, d.score)
        # PR: keep the point at which each failure is found (recall steps
        # up); thinning by position would draw false straight lines
        rc, pr = rc[::-1], pr[::-1]
        keep = np.r_[True, np.diff(rc) > 0]
        out["curves"][f"{m}|{h}"] = {
            "roc": thin(fpr, tpr),
            "pr": [[round(float(a), 4), round(float(b), 4)]
                   for a, b in zip(rc[keep], pr[keep])]}

# model file sizes (static, horizon 1-3)
for m in ["logreg", "rf", "xgb", "ebm"]:
    sizes = []
    for h in (1, 2, 3):
        p = os.path.join(SRC, "models", f"{m}_static_h{h}.joblib")
        sizes.append(os.path.getsize(p) / 1e6)
    out["size_mb"][m] = [round(s, 2) for s in sizes]

# balanced accuracy at a threshold chosen on the validation years only
# (Youden's J), so it can be set beside studies that report that metric
for m in ["altman_z", "logreg", "rf", "xgb", "ebm"]:
    f = "-" if m == "altman_z" else "static"
    d = preds[(preds.model == m) & (preds.features == f) & (preds.horizon == 1)]
    va, te = d[d.split == "val"], d[d.split == "test"]
    fpr, tpr, thr = roc_curve(va.y, va.score)
    t = thr[int(np.argmax(tpr - fpr))]
    ba = balanced_accuracy_score(te.y, (te.score >= t).astype(int))
    out["balanced_acc"][m] = round(float(ba), 4)

with open(OUT, "w") as fh:
    json.dump(out, fh, separators=(",", ":"))
print("wrote", OUT, os.path.getsize(OUT) // 1024, "KB")
print(out["size_mb"], out["balanced_acc"])
