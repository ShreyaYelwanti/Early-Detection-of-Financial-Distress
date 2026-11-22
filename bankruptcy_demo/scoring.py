"""Scoring helpers for the demo (no Streamlit import, so they are testable)."""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
HORIZONS = (1, 2, 3)

# percentile of the 2015-2018 test scores -> risk tier
TIERS = [(98, "Very high"), (95, "High"), (90, "Elevated"), (80, "Moderate"),
         (0, "Low")]


def load_calibration():
    with open(os.path.join(ASSETS, "calibration.json")) as f:
        raw = json.load(f)
    return {int(k): v for k, v in raw.items()}


def load_reference():
    """Healthy-company reference values (training years): median, p10, p90."""
    with open(os.path.join(ASSETS, "reference_stats.json")) as f:
        return json.load(f)


def load_bundles():
    """Load the three saved XGBoost models (static feature set, h = 1, 2, 3)."""
    import joblib
    return {h: joblib.load(os.path.join(ASSETS, f"xgb_static_h{h}.joblib"))
            for h in HORIZONS}


def predict_with_contrib(bundle, X):
    """Score every row of X.

    Returns (scores, contributions, bias). Contributions are exact TreeSHAP
    values in log-odds units (one column per feature), computed the same way
    as in Step 5 of the project (XGBoost pred_contribs).
    """
    import xgboost as xgb
    model, cols = bundle["model"], bundle["cols"]
    X = X[cols]
    scores = np.asarray(model.predict_proba(X)[:, 1], dtype=float)
    try:
        it_range = (0, int(model.best_iteration) + 1)
    except Exception:
        it_range = (0, 0)
    c = model.get_booster().predict(
        xgb.DMatrix(X, missing=np.nan), pred_contribs=True,
        iteration_range=it_range)
    return scores, c[:, :-1], c[:, -1]


def percentile_of(cal, h, score):
    """Percentile (0-100) of a score among the 2015-2018 test scores."""
    q = np.asarray(cal[h]["quantiles"])
    return np.interp(score, q, np.linspace(0, 100, len(q)))


def tier_of(pct):
    for cut, name in TIERS:
        if pct >= cut:
            return name
    return "Low"


def observed_rate(cal, h, score):
    """Test-year failure rate among firm-years with a similar score."""
    bins = cal[h]["bins"]
    for b in bins:
        if score < b["score_hi"] or b is bins[-1]:
            return b
    return bins[-1]
