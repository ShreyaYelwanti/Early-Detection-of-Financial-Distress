"""Static feature construction for the demo.

Mirrors Step 3 of the project: ratios from raw accounting values, clipped at
the 1st/99th percentile bounds learned on the TRAINING years only
(assets/winsor_bounds.json). Dynamics (change) features are not used here
because they need previous years' statements.
"""
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))

# Raw inputs the user provides (all in the same currency unit, e.g. USD millions)
RAW_FIELDS = [
    ("current_assets", "Current assets"),
    ("inventory", "Inventory"),
    ("total_receivables", "Total receivables"),
    ("total_assets", "Total assets"),
    ("current_liabilities", "Total current liabilities"),
    ("long_term_debt", "Long-term debt"),
    ("total_liabilities", "Total liabilities"),
    ("retained_earnings", "Retained earnings"),
    ("net_sales", "Net sales (revenue)"),
    ("cogs", "Cost of goods sold"),
    ("gross_profit", "Gross profit"),
    ("operating_expenses", "Total operating expenses"),
    ("ebitda", "EBITDA"),
    ("ebit", "EBIT"),
    ("net_income", "Net income"),
    ("market_value", "Market value (market capitalisation)"),
]

with open(os.path.join(HERE, "assets", "winsor_bounds.json")) as f:
    BOUNDS = json.load(f)
GROUPS = pd.read_csv(os.path.join(HERE, "assets", "feature_groups.csv"),
                     index_col=0)["group"]
STATIC_COLS = GROUPS[GROUPS != "dynamics"].index.tolist()


def _div(a, b):
    b = b.where(b > 0)
    return (a / b).replace([np.inf, -np.inf], np.nan)


def build_static_features(raw: pd.DataFrame) -> pd.DataFrame:
    """raw: DataFrame with the RAW_FIELDS columns -> clipped static features."""
    ca, cl = raw.current_assets, raw.current_liabilities
    ta, tl = raw.total_assets, raw.total_liabilities
    sales = raw.net_sales
    f = pd.DataFrame(index=raw.index)
    # liquidity
    f["current_ratio"] = _div(ca, cl)
    f["quick_ratio"] = _div(ca - raw.inventory, cl)
    f["wc_ta"] = _div(ca - cl, ta)
    # leverage
    f["tl_ta"] = _div(tl, ta)
    f["ltd_ta"] = _div(raw.long_term_debt, ta)
    f["cl_ta"] = _div(cl, ta)
    # profitability
    f["roa"] = _div(raw.net_income, ta)
    f["ebit_ta"] = _div(raw.ebit, ta)
    f["ebitda_ta"] = _div(raw.ebitda, ta)
    f["re_ta"] = _div(raw.retained_earnings, ta)
    f["ebit_margin"] = _div(raw.ebit, sales)
    f["ebitda_margin"] = _div(raw.ebitda, sales)
    f["gross_margin"] = _div(raw.gross_profit, sales)
    f["net_margin"] = _div(raw.net_income, sales)
    # activity
    f["asset_turnover"] = _div(sales, ta)
    f["inventory_ta"] = _div(raw.inventory, ta)
    f["receivables_ta"] = _div(raw.total_receivables, ta)
    f["receivables_sales"] = _div(raw.total_receivables, sales)
    f["cogs_sales"] = _div(raw.cogs, sales)
    f["opex_sales"] = _div(raw.operating_expenses, sales)
    # market / size
    f["mv_tl"] = _div(raw.market_value, tl)
    f["mv_ta"] = _div(raw.market_value, ta)
    f["log_assets"] = np.log(ta.where(ta > 0))
    f["log_sales"] = np.log(sales.where(sales > 0))
    f["log_mv"] = np.log(raw.market_value.where(raw.market_value > 0))
    f = f.replace([np.inf, -np.inf], np.nan)
    for c in f.columns:
        lo, hi = BOUNDS[c]
        f[c] = f[c].clip(lo, hi)
    return f[STATIC_COLS]


def altman_z(f: pd.DataFrame) -> pd.Series:
    """Altman (1968) Z from the clipped ratios, as in Step 3."""
    return (1.2 * f.wc_ta + 1.4 * f.re_ta + 3.3 * f.ebit_ta
            + 0.6 * f.mv_tl + 1.0 * f.asset_turnover)


def altman_zone(z: float) -> str:
    if pd.isna(z):
        return "n/a"
    if z < 1.81:
        return "Distress zone (Z < 1.81)"
    if z < 2.99:
        return "Grey zone (1.81 - 2.99)"
    return "Safe zone (Z > 2.99)"
