"""Quick self-test that needs only pandas/numpy (no xgboost, no streamlit).

It swaps the real XGBoost predictor for a random stand-in, so it checks the
data handling, column matching and explanation text, not the model itself.
"""
import numpy as np
import pandas as pd

from analysis import (RAW_KEYS, auto_map, explain, features_table,
                      guess_id_columns, prepare_raw, run_analysis,
                      summary_table)
from features import STATIC_COLS
from scoring import HORIZONS, load_calibration, load_reference

cal, ref = load_calibration(), load_reference()
rng = np.random.default_rng(0)


def stub_predictor(bundle, X):
    n = len(X)
    q = np.asarray(cal[1]["quantiles"])
    scores = rng.choice(q, size=n)
    contrib = rng.normal(scale=0.5, size=(n, len(STATIC_COLS)))
    return scores, contrib, np.zeros(n)


# 1) a file with the original X1..X18 column names
s = pd.read_csv("assets/demo_companies.csv")
xmap = {"current_assets": "X1", "cogs": "X2", "inventory": "X5",
        "net_income": "X6", "total_receivables": "X7",
        "market_value": "X8", "net_sales": "X9", "total_assets": "X10",
        "long_term_debt": "X11", "ebit": "X12", "gross_profit": "X13",
        "current_liabilities": "X14", "retained_earnings": "X15",
        "total_liabilities": "X17", "operating_expenses": "X18",
        "ebitda": "X4"}
up = s[["company_name", "year"] + RAW_KEYS].rename(columns=xmap)
m = auto_map(up.columns)
assert all(m[k] is not None for k in RAW_KEYS), m
print("X-name mapping OK:", sum(v is not None for v in m.values()), "/ 16")

# 2) a file with Compustat-style names and messy text numbers
comp = pd.DataFrame({"Firm Name": ["A", "B", "C"], "fyear": [2020, 2020, 2020],
                     "AT": ["1,200.5", "300", "0"], "ACT": [400, 100, 5],
                     "LCT": [300, 150, 2], "LT": [800, 280, 1],
                     "RE": [-50, -200, 0], "SALE": [900, 120, 3],
                     "EBIT": [60, -40, 0], "NI": [20, -60, 0],
                     "MKVALT": [500, 30, 0]})
m2 = auto_map(comp.columns)
print("Compustat mapping found:", [k for k, v in m2.items() if v])
print("missing:", [k for k, v in m2.items() if v is None])
cc, yc = guess_id_columns(comp.columns)
print("id columns:", cc, yc)
raw, labels = prepare_raw(comp, m2, cc, yc)
res = run_analysis(raw, labels, {h: None for h in HORIZONS}, cal,
                   predictor=stub_predictor)
print("skipped rows (assets <= 0):", res["skipped"])
print(summary_table(res).to_string(index=False))

# 3) explanations and the features table
r, l = explain(res, 0, 1, ref)
print("\nRAISING:", *r, sep="\n- ")
print("\nLOWERING:", *l, sep="\n- ")
ft = features_table(res, 0, 1, ref)
print("\nfeatures table:", ft.shape, list(ft.columns))

# 4) the demo sample file end to end
raw, labels = prepare_raw(s, auto_map(s.columns), "company_name", "year")
res = run_analysis(raw, labels, {h: None for h in HORIZONS}, cal,
                   predictor=stub_predictor)
print("\nsample file rows analysed:", len(res["labels"]),
      "| skipped:", len(res["skipped"]))
print("OK")

# 5) structured explanation and page components (new design)
import ui
from features import altman_zone
from scoring import observed_rate

ex = analysis_ex = None
from analysis import explain_structured
ex = explain_structured(res, 0, 1, ref)
assert ex["raising"] and ex["lowering"] and len(ex["groups"]) == 5
rows = [{"h": h, "tier": res["h"][h]["tier"][0],
         "pct": float(res["h"][h]["pct"][0])} for h in HORIZONS]
parts = [
    ui.verdict("<b>x</b> Co, 2017", rows, float(res["z"][0]),
               altman_zone(res["z"][0]), cal[1]["n"], "failed 1 year(s) later"),
    ui.group_bars(ex["groups"]),
    ui.factors(ex["raising"], "up"), ui.factors(ex["lowering"], "down"),
    ui.callout(ui.summary_sentence(ex["raising"], ex["lowering"])),
    ui.tier_stack({"Low": 5, "High": 1}),
]
for p in parts:
    assert "\n" not in p, "HTML must be one line (Markdown code-block risk)"
assert "<b>x</b>" not in parts[0], "names must be escaped"
print("UI components OK")
