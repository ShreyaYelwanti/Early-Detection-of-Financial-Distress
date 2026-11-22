"""Analysis logic for the demo: column matching, batch scoring and
plain-language explanations. No Streamlit import, so it can be tested."""
import re

import numpy as np
import pandas as pd

from features import (GROUPS, RAW_FIELDS, STATIC_COLS, altman_z, altman_zone,
                      build_static_features)
from scoring import HORIZONS, percentile_of, predict_with_contrib, tier_of

RAW_KEYS = [k for k, _ in RAW_FIELDS]
LABELS = dict(RAW_FIELDS)
MAX_ROWS = 5000

# ----------------------------------------------------------- column matching
# Original column names of the American bankruptcy dataset (X1..X18)
XMAP = {
    "x1": "current_assets", "x2": "cogs", "x4": "ebitda", "x5": "inventory",
    "x6": "net_income", "x7": "total_receivables", "x8": "market_value",
    "x9": "net_sales", "x10": "total_assets", "x11": "long_term_debt",
    "x12": "ebit", "x13": "gross_profit", "x14": "current_liabilities",
    "x15": "retained_earnings", "x17": "total_liabilities",
    "x18": "operating_expenses",
}
# Other common spellings, including Compustat tickers
ALIASES = {
    "current_assets": ["currentassets", "totalcurrentassets", "act"],
    "inventory": ["inventory", "inventories", "invt"],
    "total_receivables": ["totalreceivables", "receivables",
                          "accountsreceivable", "rect"],
    "total_assets": ["totalassets", "assets", "at"],
    "current_liabilities": ["currentliabilities", "totalcurrentliabilities",
                            "lct"],
    "long_term_debt": ["longtermdebt", "totallongtermdebt", "ltdebt",
                       "dltt"],
    "total_liabilities": ["totalliabilities", "liabilities", "lt"],
    "retained_earnings": ["retainedearnings", "re"],
    "net_sales": ["netsales", "sales", "sale", "revenue", "totalrevenue",
                  "revt"],
    "cogs": ["cogs", "costofgoodssold", "costofrevenue"],
    "gross_profit": ["grossprofit", "gp"],
    "operating_expenses": ["operatingexpenses", "totaloperatingexpenses",
                           "opex", "xopr"],
    "ebitda": ["ebitda", "oibdp"],
    "ebit": ["ebit", "operatingincome", "oiadp"],
    "net_income": ["netincome", "netprofit", "profitaftertax", "ni"],
    "market_value": ["marketvalue", "marketcap", "marketcapitalisation",
                     "marketcapitalization", "mkvalt"],
}


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def auto_map(columns):
    """Guess which uploaded column holds each required field."""
    by_norm = {}
    for c in columns:
        by_norm.setdefault(_norm(c), c)
    mapping = {k: None for k in RAW_KEYS}
    # 1) the original X1..X18 naming of the American dataset
    xhits = {k: by_norm[x] for x, k in XMAP.items() if x in by_norm}
    if len(xhits) >= 8:
        mapping.update(xhits)
    # 2) names and aliases
    for k in RAW_KEYS:
        if mapping[k] is not None:
            continue
        for cand in [_norm(k), _norm(LABELS[k])] + ALIASES.get(k, []):
            if cand in by_norm:
                mapping[k] = by_norm[cand]
                break
    return mapping


def guess_id_columns(columns):
    """Guess the company-name and year columns (both optional)."""
    comp = year = None
    for c in columns:
        n = _norm(c)
        if comp is None and any(t in n for t in
                                ("company", "firm", "name", "ticker", "id")):
            comp = c
        if year is None and n in ("year", "fyear", "fiscalyear", "date"):
            year = c
    return comp, year


def _to_num(s):
    return pd.to_numeric(s.astype(str).str.replace(",", "", regex=False)
                         .str.strip(), errors="coerce")


def prepare_raw(df, mapping, company_col=None, year_col=None):
    """Build the 16-column raw table and row labels from an uploaded table."""
    df = df.reset_index(drop=True)
    raw = pd.DataFrame({k: (_to_num(df[mapping[k]]) if mapping.get(k)
                            else np.nan) for k in RAW_KEYS})
    labels = []
    for i in range(len(df)):
        name = (str(df.loc[i, company_col]) if company_col
                else f"Row {i + 1}")
        if year_col:
            name += f" ({df.loc[i, year_col]})"
        labels.append(name)
    return raw, labels


# ------------------------------------------------------------ feature texts
FEATURE_INFO = {
    "current_ratio": ("Current ratio", "current assets / current liabilities",
                      "low", "Few short-term assets to cover short-term "
                      "bills."),
    "quick_ratio": ("Quick ratio",
                    "(current assets - inventory) / current liabilities",
                    "low", "Little cash-like money to cover short-term "
                    "debts."),
    "wc_ta": ("Working capital / assets",
              "(current assets - current liabilities) / total assets", "low",
              "A thin cushion of short-term assets over short-term debts."),
    "tl_ta": ("Debt ratio", "total liabilities / total assets", "high",
              "The company is financed mostly by borrowed money."),
    "ltd_ta": ("Long-term debt / assets", "long-term debt / total assets",
               "high", "A heavy long-term debt burden."),
    "cl_ta": ("Current liabilities / assets",
              "current liabilities / total assets", "high",
              "A large share of assets is owed in the short term."),
    "roa": ("Return on assets", "net income / total assets", "low",
            "The company earns little or loses money relative to its size."),
    "ebit_ta": ("EBIT / assets", "EBIT / total assets", "low",
                "Weak operating earnings relative to size."),
    "ebitda_ta": ("EBITDA / assets", "EBITDA / total assets", "low",
                  "Weak cash-like operating earnings relative to size."),
    "re_ta": ("Retained earnings / assets",
              "retained earnings / total assets", "low",
              "Little profit has been kept, or losses have piled up."),
    "ebit_margin": ("EBIT margin", "EBIT / net sales", "low",
                    "Sales produce little operating profit."),
    "ebitda_margin": ("EBITDA margin", "EBITDA / net sales", "low",
                      "Sales produce little operating cash profit."),
    "gross_margin": ("Gross margin", "gross profit / net sales", "low",
                     "Little profit is left after production costs."),
    "net_margin": ("Net margin", "net income / net sales", "low",
                   "Little or no profit is left from each unit of sales."),
    "asset_turnover": ("Asset turnover", "net sales / total assets", "low",
                       "Assets generate little sales."),
    "inventory_ta": ("Inventory / assets", "inventory / total assets",
                     "high", "Money is tied up in unsold stock."),
    "receivables_ta": ("Receivables / assets",
                       "total receivables / total assets", "high",
                       "A lot of money is still owed by customers."),
    "receivables_sales": ("Receivables / sales",
                          "total receivables / net sales", "high",
                          "Customers may be slow to pay."),
    "cogs_sales": ("Cost of goods sold / sales", "COGS / net sales", "high",
                   "Production costs absorb most of the revenue."),
    "opex_sales": ("Operating expenses / sales",
                   "operating expenses / net sales", "high",
                   "Operating costs are heavy relative to sales."),
    "mv_tl": ("Market value / liabilities",
              "market value / total liabilities", "low",
              "The market values the company low compared with its debts."),
    "mv_ta": ("Market value / assets", "market value / total assets", "low",
              "The market values the company low compared with its assets."),
    "log_assets": ("Company size (assets)", "ln(total assets)", "low",
                   "Smaller companies failed more often in the training "
                   "data."),
    "log_sales": ("Company size (sales)", "ln(net sales)", "low",
                  "Companies with lower sales failed more often in the "
                  "training data."),
    "log_mv": ("Company size (market value)", "ln(market value)", "low",
               "Companies with a low market value failed more often in the "
               "training data."),
}


# plain names for the five feature groups
GROUP_NAMES = {
    "liquidity": "Short-term cash cushion",
    "leverage": "Debt load",
    "profitability": "Profitability",
    "activity": "Operating efficiency",
    "market_size": "Market value and size",
}


def _fmt(v):
    return "not provided" if pd.isna(v) else f"{v:.2f}"


# --------------------------------------------------------------- analysis
def run_analysis(raw, labels, bundles, cal, predictor=predict_with_contrib):
    """Score every valid row at all horizons. Rows need total assets > 0."""
    raw = raw.reset_index(drop=True)
    valid = (raw.total_assets > 0).fillna(False).values
    skipped = [labels[i] for i in range(len(raw)) if not valid[i]]
    raw_v = raw[valid].reset_index(drop=True)
    labels_v = [labels[i] for i in range(len(raw)) if valid[i]]
    if raw_v.empty:
        return None
    feat = build_static_features(raw_v)
    res = {"raw": raw_v, "feat": feat, "labels": labels_v,
           "skipped": skipped, "z": altman_z(feat).values, "h": {},
           "n_missing": feat.isna().sum(axis=1).values}
    for h in HORIZONS:
        sc, contrib = predictor(bundles[h], feat)[:2]
        pct = np.asarray(percentile_of(cal, h, sc))
        res["h"][h] = {"score": np.asarray(sc), "contrib": np.asarray(contrib),
                       "pct": pct, "tier": [tier_of(p) for p in pct]}
    return res


def summary_table(res):
    h1 = res["h"][1]["contrib"]
    top = [FEATURE_INFO[STATIC_COLS[j]][0] for j in h1.argmax(axis=1)]
    d = pd.DataFrame({"Company": res["labels"]})
    for h in HORIZONS:
        d[f"Risk: {h} yr"] = res["h"][h]["tier"]
    for h in HORIZONS:
        d[f"Percentile {h} yr"] = res["h"][h]["pct"].round(1)
    d["Altman Z"] = np.round(res["z"], 2)
    d["Altman zone"] = [altman_zone(z).split(" (")[0] for z in res["z"]]
    d["Biggest risk driver (1 yr)"] = top
    return d


def features_table(res, i, h, ref):
    c = res["h"][h]["contrib"][i]
    v = res["feat"].iloc[i]
    rows = []
    for j, col in enumerate(STATIC_COLS):
        label, formula, _, _ = FEATURE_INFO[col]
        r = ref[col]
        eff = ("raises risk" if c[j] > 0.02 else
               "lowers risk" if c[j] < -0.02 else "neutral")
        rows.append({"Group": GROUPS[col], "Feature": label,
                     "How it is computed": formula,
                     "Your value": None if pd.isna(v[col]) else round(v[col], 3),
                     "Healthy firms (middle 80%)":
                         f"{r['p10']:.2f} to {r['p90']:.2f}",
                     "Healthy median": round(r["median"], 3),
                     "Contribution": round(float(c[j]), 3), "Effect": eff})
    return (pd.DataFrame(rows).assign(_a=lambda d: d.Contribution.abs())
            .sort_values("_a", ascending=False).drop(columns="_a"))


def _strength(share):
    return "Major" if share >= 0.15 else "Notable" if share >= 0.07 else "Minor"


def _position(col, val, ref):
    """Where a value sits relative to typical healthy companies."""
    if pd.isna(val):
        return "missing"
    med, lo, hi = ref[col]["median"], ref[col]["p10"], ref[col]["p90"]
    if abs(val - med) <= 0.05 * max(hi - lo, 1e-9):
        return "typical"
    below = val < med
    risky_low = FEATURE_INFO[col][2] == "low"
    return "risky" if below == risky_low else "safe"


def explain(res, i, h, ref, n_raise=4, n_lower=3):
    """Plain-language reasons for one company and one horizon."""
    c = res["h"][h]["contrib"][i]
    v = res["feat"].iloc[i]
    total = float(np.abs(c).sum()) or 1.0
    order = np.argsort(-c)
    raise_idx = [j for j in order if c[j] > 0][:n_raise]
    lower_idx = [j for j in order[::-1] if c[j] < 0][:n_lower]

    def intro(col):
        return (f"**{FEATURE_INFO[col][0]}** is {_fmt(v[col])} (typical "
                f"healthy company: {ref[col]['median']:.2f}). ")

    raising, lowering = [], []
    for j in raise_idx:
        col = STATIC_COLS[j]
        pos = _position(col, v[col], ref)
        if pos == "risky":
            why = FEATURE_INFO[col][3]
        elif pos == "missing":
            why = ("This input was not provided, so the model treated it as "
                   "unknown, which it associates with higher risk.")
        else:
            why = ("The value itself is not unusual, but together with the "
                   "other ratios the model reads it as risk-raising.")
        raising.append(f"{_strength(abs(c[j]) / total)} factor: "
                       + intro(col) + why)
    for j in lower_idx:
        col = STATIC_COLS[j]
        pos = _position(col, v[col], ref)
        if pos == "safe":
            why = "This is on the healthy side, which lowers the risk."
        elif pos == "missing":
            why = ("This input was not provided, so the model treated it as "
                   "unknown, which it associates with lower risk.")
        else:
            why = ("The value is close to typical, and together with the "
                   "other ratios the model reads it as lowering the risk.")
        lowering.append(f"{_strength(abs(c[j]) / total)} protective factor: "
                        + intro(col) + why)
    return raising, lowering


def explain_structured(res, i, h, ref, n_raise=4, n_lower=3):
    """Same idea as explain(), but returns data the page can draw.

    Returns {"raising": [...], "lowering": [...], "groups": [(name, effect)]}.
    Every factor is a dict with the label, the company's value, the healthy
    range (p10 to p90), the median, its share of the total influence and a
    one-sentence reason.
    """
    c = res["h"][h]["contrib"][i]
    v = res["feat"].iloc[i]
    total = float(np.abs(c).sum()) or 1.0
    order = np.argsort(-c)
    raise_idx = [j for j in order if c[j] > 0][:n_raise]
    lower_idx = [j for j in order[::-1] if c[j] < 0][:n_lower]

    def make(j, up):
        col = STATIC_COLS[j]
        pos = _position(col, v[col], ref)
        if up:
            if pos == "risky":
                why = FEATURE_INFO[col][3]
            elif pos == "missing":
                why = ("Not provided, so the model treated it as unknown. In "
                       "the training data, unknown values went with higher "
                       "risk.")
            else:
                why = ("On its own this value looks ordinary. The model "
                       "flags it because of how it combines with the other "
                       "numbers.")
        else:
            if pos == "safe":
                why = ("This is on the healthy side of the typical range, "
                       "which lowers the risk.")
            elif pos == "missing":
                why = ("Not provided, so the model treated it as unknown. In "
                       "the training data, unknown values went with lower "
                       "risk.")
            else:
                why = ("This value is close to typical. The model counts it "
                       "in the company's favour in combination with the "
                       "other numbers.")
        r = ref[col]
        share = abs(float(c[j])) / total
        return {"col": col, "label": FEATURE_INFO[col][0],
                "formula": FEATURE_INFO[col][1],
                "value": None if pd.isna(v[col]) else float(v[col]),
                "median": float(r["median"]), "lo": float(r["p10"]),
                "hi": float(r["p90"]), "share": share,
                "strength": _strength(share), "why": why, "position": pos}

    g = (pd.Series(c, index=STATIC_COLS)
         .groupby([GROUPS[x] for x in STATIC_COLS]).sum())
    groups = sorted(((GROUP_NAMES.get(k, k), float(val))
                     for k, val in g.items()), key=lambda t: -t[1])
    return {"raising": [make(j, True) for j in raise_idx],
            "lowering": [make(j, False) for j in lower_idx],
            "groups": groups}
