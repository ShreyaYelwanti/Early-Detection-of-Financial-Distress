"""Early Detection of Financial Distress (Streamlit demo).

Give it a company's financial statements and it estimates the risk of
bankruptcy within 1, 2 and 3 years, then shows which numbers drove the result.

Run:  python -m streamlit run app.py
"""
import os
import re

import numpy as np
import pandas as pd
import streamlit as st

import ui
from analysis import (FEATURE_INFO, LABELS, MAX_ROWS, RAW_KEYS, auto_map,
                      explain_structured, features_table, guess_id_columns,
                      prepare_raw, run_analysis, summary_table)
from features import altman_zone
from scoring import (HORIZONS, load_bundles, load_calibration,
                     load_reference, observed_rate)

HERE = os.path.dirname(os.path.abspath(__file__))
hz = ui.hz

st.set_page_config(page_title="Early detection of financial distress",
                   layout="wide", initial_sidebar_state="expanded")
ui.inject_css()

# Input fields, grouped the way a person reads financial statements
FIELD_GROUPS = [
    ("Balance sheet", ["total_assets", "current_assets", "inventory",
                       "total_receivables", "current_liabilities",
                       "long_term_debt", "total_liabilities",
                       "retained_earnings"]),
    ("Income statement", ["net_sales", "cogs", "gross_profit",
                          "operating_expenses", "ebitda", "ebit",
                          "net_income"]),
    ("Stock market", ["market_value"]),
]


@st.cache_resource
def get_models():
    return load_bundles()


@st.cache_data
def get_static():
    cal, ref = load_calibration(), load_reference()
    s = pd.read_csv(os.path.join(HERE, "assets", "demo_companies.csv"))
    return cal, ref, s


bundles = get_models()
cal, ref, samples = get_static()
N_TEST = cal[1]["n"]


@st.cache_resource
def score_samples():
    """Score the bundled example companies once, to order the examples."""
    raw = samples[RAW_KEYS].copy()
    labels = [f"{r.company_name}, {r.year}" for r in samples.itertuples()]
    return run_analysis(raw, labels, bundles, cal)


def start_analysis(raw, labels, notes=None):
    res = run_analysis(raw, labels, bundles, cal)
    if res is None:
        st.sidebar.error("No valid rows: every row needs total assets "
                         "greater than zero.")
        return
    if notes is not None:
        valid = (raw.reset_index(drop=True).total_assets > 0).fillna(False).values
        res["notes"] = [n for n, ok in zip(notes, valid) if ok]
    else:
        res["notes"] = None
    st.session_state["res"] = res
    st.session_state.pop("pick", None)


def example_row(idx):
    r = samples.iloc[[idx]]
    start_analysis(r[RAW_KEYS], [f"{r.company_name.iloc[0]}, {r.year.iloc[0]}"],
                   notes=[r.note.iloc[0]])


# ------------------------------------------- first visit: show a real example
if "res" not in st.session_state:
    sc = score_samples()
    failed = np.where(samples.note.values == "failed 1 year(s) later")[0]
    best = failed[int(np.argmax(sc["h"][1]["pct"][failed]))]
    example_row(int(best))

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown('<div class="side-title">Company data</div>'
                '<p class="side-note">All amounts in USD millions, one '
                'fiscal year per company.</p>', unsafe_allow_html=True)
    tab_ex, tab_type, tab_up = st.tabs(["Examples", "Type in", "Upload"])

    # --- examples
    with tab_ex:
        st.caption("Real companies from the 2015-2018 test years, with names "
                   "hidden. We know what happened to each one afterwards.")
        kind = st.radio("Show companies that", ["Failed later", "Stayed healthy"],
                        horizontal=True)
        sc = score_samples()
        is_failed = samples.note.str.startswith("failed").values
        idxs = np.where(is_failed if kind == "Failed later" else ~is_failed)[0]
        idxs = idxs[np.argsort(-sc["h"][1]["pct"][idxs])]
        def ex_label(i):
            r = samples.iloc[i]
            m = re.match(r"failed (\d) year", r.note)
            what = ("stayed healthy" if r.note == "never failed"
                    else f"failed {m.group(1)} yr later")
            return f"{r.company_name}, {r.year} ({what})"
        pick = st.selectbox("Company", idxs, format_func=ex_label,
                            help="Sorted from the highest to the lowest "
                                 "1-year risk score.")
        if st.button("Analyze this company", type="primary", key="go_ex"):
            example_row(int(pick))

    # --- manual entry
    with tab_type:
        healthy = samples[samples.note == "never failed"][RAW_KEYS].median()
        for k in RAW_KEYS:
            st.session_state.setdefault(f"man_{k}", float(round(healthy[k], 3)))
        st.caption("The boxes start with a typical healthy company. Replace "
                   "them with your own numbers.")
        with st.form("manual_form"):
            name = st.text_input("Company name", "My company")
            for title, keys in FIELD_GROUPS:
                st.markdown(f'<div class="mini">{title}</div>',
                            unsafe_allow_html=True)
                for k in keys:
                    st.number_input(LABELS[k], key=f"man_{k}", format="%.3f",
                                    step=1.0)
            go_manual = st.form_submit_button("Analyze these numbers",
                                              type="primary")
        if go_manual:
            raw = pd.DataFrame([{k: st.session_state[f"man_{k}"]
                                 for k in RAW_KEYS}])
            start_analysis(raw, [name or "My company"])

    # --- file upload
    with tab_up:
        st.caption("One row per company and year (CSV or Excel). Column names "
                   "are matched automatically and you can correct any match.")
        tmpl = samples[["company_name", "year"] + RAW_KEYS].head(3)
        st.download_button("Download a CSV template",
                           tmpl.to_csv(index=False).encode(),
                           file_name="template.csv", mime="text/csv")
        up = st.file_uploader("Your file", type=["csv", "xlsx", "xls"])
        if up is not None:
            df = None
            try:
                df = (pd.read_csv(up) if up.name.lower().endswith(".csv")
                      else pd.read_excel(up))
                df.columns = [str(c) for c in df.columns]
            except Exception as e:
                st.error(f"Could not read the file: {e}. For Excel files you "
                         "may need `python -m pip install openpyxl`.")
            if df is not None:
                if len(df) > MAX_ROWS:
                    st.warning(f"Only the first {MAX_ROWS} rows are analysed.")
                    df = df.head(MAX_ROWS)
                st.caption(f"{len(df)} rows and {df.shape[1]} columns read.")
                auto = auto_map(list(df.columns))
                comp0, year0 = guess_id_columns(list(df.columns))
                options = ["(not provided)"] + list(df.columns)
                n_found = sum(v is not None for v in auto.values())
                if n_found == 16:
                    st.success("All 16 required columns were found.")
                with st.expander(f"Check column matching ({n_found} of 16 found)",
                                 expanded=n_found < 16):
                    mapping = {}
                    for k in RAW_KEYS:
                        idx = options.index(auto[k]) if auto[k] in options else 0
                        sel = st.selectbox(LABELS[k], options, index=idx,
                                           key=f"map_{up.name}_{k}")
                        mapping[k] = None if sel == "(not provided)" else sel
                    sel = st.selectbox(
                        "Company name column (optional)", options,
                        index=options.index(comp0) if comp0 in options else 0,
                        key=f"comp_{up.name}")
                    comp_col = None if sel == "(not provided)" else sel
                    sel = st.selectbox(
                        "Year column (optional)", options,
                        index=options.index(year0) if year0 in options else 0,
                        key=f"year_{up.name}")
                    year_col = None if sel == "(not provided)" else sel
                missing = [LABELS[k] for k in RAW_KEYS if mapping[k] is None]
                if missing:
                    st.warning("Not provided: " + ", ".join(missing) +
                               ". Ratios that need them stay blank, so the "
                               "result is less reliable.")
                if mapping["total_assets"] is None:
                    st.error("Total assets is required. Please match it above.")
                elif st.button("Analyze this file", type="primary",
                               key="go_file"):
                    raw, labels = prepare_raw(df, mapping, comp_col, year_col)
                    start_analysis(raw, labels)

# --------------------------------------------------------------------- hero
st.markdown(ui.masthead(
    "Early detection of financial distress",
    "Enter a company's financial statements. A machine-learning model "
    "estimates how likely the company is to go bankrupt within 1, 2 or 3 "
    "years, then shows which of its numbers drove that answer."),
    unsafe_allow_html=True)

res = st.session_state["res"]
n = len(res["labels"])

# ------------------------------------------------- many companies: overview
if res["skipped"]:
    st.warning(f"Skipped {len(res['skipped'])} row(s) without positive total "
               "assets.")

if n > 1:
    st.markdown(ui.section(
        f"Overview of {n} companies",
        "Risk tier at the 1-year horizon. Sort the table by clicking a "
        "column heading, then pick a company below to see why."),
        unsafe_allow_html=True)
    counts = pd.Series(res["h"][1]["tier"]).value_counts().to_dict()
    st.markdown(ui.tier_stack(counts), unsafe_allow_html=True)
    table = summary_table(res)
    shown = table.sort_values("Percentile 1 yr", ascending=False)
    cfg = {f"Percentile {h} yr": st.column_config.ProgressColumn(
        f"Rank {h} yr", min_value=0, max_value=100, format="%.0f")
        for h in HORIZONS}
    st.dataframe(shown, hide_index=True, column_config=cfg)
    st.download_button("Download results (CSV)",
                       table.to_csv(index=False).encode(),
                       file_name="distress_results.csv", mime="text/csv")
    default_i = int(np.argmax(res["h"][1]["pct"]))
    i = st.selectbox("Look closer at", list(range(n)), index=default_i,
                     format_func=lambda x: res["labels"][x], key="pick")
else:
    i = 0

n_sparse = int((res["n_missing"] > 6).sum())
if n_sparse:
    st.warning(f"{n_sparse} row(s) have more than 6 of the 25 ratios missing "
               "because of blank or zero inputs. Treat those results with "
               "extra caution.")

# ------------------------------------------------------------------ verdict
rows = [{"h": h, "tier": res["h"][h]["tier"][i],
         "pct": float(res["h"][h]["pct"][i])} for h in HORIZONS]
note = res["notes"][i] if res.get("notes") else None
st.markdown(ui.verdict(res["labels"][i], rows, float(res["z"][i]),
                       altman_zone(res["z"][i]), N_TEST, note),
            unsafe_allow_html=True)

# ---------------------------------------------------------------------- why
st.markdown(ui.section(
    "Why this result?",
    "The model looks at 25 ratios built from the statements. For each one it "
    "works out whether the company's value pushes the risk up or down. "
    "Pick a time window to see that window's reasons."),
    unsafe_allow_html=True)
h = st.radio("Time window", HORIZONS, horizontal=True,
             format_func=lambda x: f"Fails within {hz(x)}",
             label_visibility="collapsed")

ex = explain_structured(res, i, h, ref)
o = observed_rate(cal, h, float(res["h"][h]["score"][i]))
st.markdown(ui.callout(
    ui.summary_sentence(ex["raising"], ex["lowering"]),
    f"In the 2015-2018 test years, {o['pos']} of {o['n']:,} companies with "
    f"a score like this one failed within {hz(h)} ({100 * o['rate']:.1f}%). "
    f"Across all test companies the rate was {100 * cal[h]['base_rate']:.1f}%."),
    unsafe_allow_html=True)

st.markdown(ui.subtitle("The big picture: five areas of the business"),
            unsafe_allow_html=True)
st.markdown(ui.group_bars(ex["groups"]), unsafe_allow_html=True)

st.markdown(ui.subtitle("What raises the risk"), unsafe_allow_html=True)
st.markdown(ui.range_key(), unsafe_allow_html=True)
st.markdown(ui.factors(ex["raising"], "up"), unsafe_allow_html=True)

st.markdown(ui.subtitle("What lowers the risk"), unsafe_allow_html=True)
st.markdown(ui.factors(ex["lowering"], "down"), unsafe_allow_html=True)

with st.expander("How are these effects calculated?"):
    st.markdown(
        """
Each factor's push comes from **SHAP values**, a standard way to split one
model prediction into a contribution per input. They are computed exactly
for tree models (TreeSHAP). Three things are useful to know:

- **They add up.** The pushes of all 25 ratios, plus a baseline, add up to
  the model's score for this company. The percentages above show each
  ratio's share of the total push, ignoring direction.
- **Direction and size are measured in log-odds**, the unit the model works
  in internally. That is why the bars have no everyday unit: longer simply
  means a bigger push.
- **The model's reasoning is not a cause.** A ratio can lift the risk
  because the model learned that it goes with failure in the past, not
  because changing it would prevent failure.
""")

# --------------------------------------------------------------- the detail
st.markdown(ui.section(
    "All the detail",
    "Every ratio the model used, and the raw numbers they came from."),
    unsafe_allow_html=True)
t_ratios, t_raw = st.tabs(["All 25 ratios", "Numbers used"])
with t_ratios:
    ft = features_table(res, i, h, ref).rename(columns={
        "Contribution": "Push on risk", "Effect": "Direction"})
    st.caption(f"Sorted by size of push for the {hz(h)} window. A positive "
               "push raises the risk, a negative push lowers it.")
    st.dataframe(ft, hide_index=True)
with t_raw:
    rawrow = res["raw"].iloc[i]
    st.dataframe(pd.DataFrame({
        "Field": [LABELS[k] for k in RAW_KEYS],
        "Value (USD millions)": [None if pd.isna(rawrow[k]) else
                                 float(rawrow[k]) for k in RAW_KEYS],
        "Status": ["missing" if pd.isna(rawrow[k]) else "used"
                   for k in RAW_KEYS]}), hide_index=True)
    st.caption("The research version of the models also uses 22 "
               "year-over-year change features. They need several years of "
               "statements per company, so this demo scores one year at a "
               "time.")

with st.expander("Limits: what this demo can and cannot tell you"):
    st.markdown(
        """
- **It learned from US-listed companies, 1999-2011** (data from Lombardo et
  al., 2022). For other countries, sectors or periods, treat the result as
  a rough indication.
- **The score is a ranking, not a probability.** The models use class
  weights, so a raw score is not a chance of failure. Read it through the
  risk tier, the rank, and the failure rate seen in the 2015-2018 test years.
- **Explanations show what the model relies on, not what causes distress.**
  Other ratios can stand in for a missing one.
- **Market value matters a lot** close to failure, because share prices
  already reflect trouble. Part of the signal is the market's opinion, not
  accounting alone.
- **Use USD millions.** The three size features use the logarithm of the
  amounts, so the wrong unit shifts the result.
""")

st.markdown(ui.foot(
    "Course project demo. Models were trained on US-listed companies "
    "(1999-2011) and tested on 2015-2018. Results are indications, not "
    "financial advice."), unsafe_allow_html=True)
