"""Model comparison: the five contenders side by side and why XGBoost."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

import compare_ui as cu
import ui

st.set_page_config(page_title="Model comparison", layout="wide",
                   initial_sidebar_state="expanded")
ui.inject_css()
cu.inject_extra_css()

data = cu.load_comparison()

st.markdown(ui.masthead(
    "Why XGBoost?",
    "Four machine-learning models and the classic Altman Z-score were "
    "trained and tested on the same data. Here is how they compare and "
    "what the choice of XGBoost rests on."), unsafe_allow_html=True)
try:
    st.page_link("app.py", label="Back to the risk predictor")
except Exception:
    pass

st.markdown(ui.callout(
    "All models saw the same split: <b>trained on 1999-2011, tuned on "
    "2012-2014, scored on 2015-2018</b>. The test years played no part in "
    "fitting.",
    "Failures are rare (about 1% of company-years at one year), so accuracy "
    "is not used. A model that said nobody fails would be right 99% of the "
    "time. The columns below measure how well failures are ranked above "
    "healthy companies."), unsafe_allow_html=True)

# ---------------------------------------------------------------- controls
c1, c2 = st.columns([2, 2])
with c1:
    h = st.radio("Warning time", [1, 2, 3], horizontal=True,
                 format_func=lambda x: f"Fails within {ui.hz(x)}")
with c2:
    feats = st.radio("Inputs used", ["static", "full"], horizontal=True,
                     format_func=lambda x: {
                         "static": "One year of statements (used by the website)",
                         "full": "Plus year-over-year changes"}[x])

look = cu.metric_lookup(data, feats)
rows = {m: look[(m, h)] for m in cu.MODEL_ORDER}
best = {k: {m for m in cu.MODEL_ORDER
            if round(rows[m][k], 3) == max(round(rows[x][k], 3)
                                           for x in cu.MODEL_ORDER)}
        for k in ("roc", "pr", "rec10", "rec5")}
pos, n = rows["xgb"]["pos"], rows["xgb"]["n"]

st.markdown(ui.section(
    "Scoreboard",
    f"Test years 2015-2018: {n:,} company-years, of which {pos} failed "
    f"within {ui.hz(h)}. The best value in each column is in bold; "
    "XGBoost's row is shaded."), unsafe_allow_html=True)
st.markdown(cu.score_table(rows, best), unsafe_allow_html=True)
st.markdown(
    '<p class="note">ROC-AUC: chance that a failed company is scored riskier '
    'than a healthy one (0.5 is a coin flip, 1.0 is perfect). PR-AUC: how '
    'clean the top of the ranking is; it depends on how rare failures are, '
    'so read it against the "x the base rate" line. Riskiest 10% / 5%: share '
    'of all failures that sit in the top-scored slice of company-years, the '
    'list an analyst could realistically review.</p>', unsafe_allow_html=True)

# ------------------------------------------------------------------ curves
st.markdown(ui.subtitle("The same comparison as curves"),
            unsafe_allow_html=True)
fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9))
for m in cu.MODEL_ORDER:
    cv = data["curves"][f"{m}|{h}"]
    lw = 2.6 if m == "xgb" else 1.5
    axes[0].plot([p[0] for p in cv["roc"]], [p[1] for p in cv["roc"]],
                 color=cu.MODEL_COLOR[m], lw=lw, label=cu.MODEL_SHORT[m])
    axes[1].plot([p[0] for p in cv["pr"]], [p[1] for p in cv["pr"]],
                 color=cu.MODEL_COLOR[m], lw=lw, label=cu.MODEL_SHORT[m])
axes[0].plot([0, 1], [0, 1], ls=":", color="#B0B8C2", lw=1)
axes[0].set(title="ROC curve (higher and further left is better)",
            xlabel="False alarm rate", ylabel="Share of failures caught")
axes[1].set(title="Precision-recall curve", xlabel="Share of failures caught",
            ylabel="Precision (share of flags that fail)", ylim=(0, 1))
for ax in axes:
    ax.grid(alpha=.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.title.set_fontsize(10)
axes[0].legend(fontsize=8, frameon=False, loc="lower right")
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)
st.markdown('<p class="note">Curves use the website\'s inputs (one year of '
            'statements) on the test years.</p>', unsafe_allow_html=True)

# --------------------------------------------------------- is the gap real?
st.markdown(ui.section(
    "Are the differences real?",
    "A small gap in a table can be noise. Each line below re-draws the test "
    "companies many times and asks whether XGBoost's ROC-AUC lead over "
    "another model holds up. These paired tests were run on the fuller input "
    "set in the notebooks."), unsafe_allow_html=True)


def paired(o, h, metric):
    for r in data["pairwise_full"]:
        if r["h"] == h and r["metric"] == metric:
            if (r["a"], r["b"]) == ("xgb", o):
                return r["delta"], r["lo"], r["hi"]
            if (r["a"], r["b"]) == (o, "xgb"):
                return -r["delta"], -r["hi"], -r["lo"]
    return None


body = []
for o in ("logreg", "rf", "ebm"):
    cells = []
    for hh in (1, 2, 3):
        d, lo, hi = paired(o, hh, "ROC_AUC")
        if lo > 0:
            v, col = "XGBoost higher", "#0F4C5C"
        elif hi < 0:
            v, col = f"{cu.MODEL_SHORT[o]} higher", "#C8452F"
        else:
            v, col = "No clear difference", "#6B7A8A"
        cells.append(
            f'<td class="num">{d:+.3f}<span class="ci">{lo:+.3f} to '
            f'{hi:+.3f}</span>{cu.badge(v, col)}</td>')
    body.append(f"<tr><td>{cu.dot(o)}XGBoost minus "
                f"{ui.esc(cu.MODEL_SHORT[o])}</td>{''.join(cells)}</tr>")
st.markdown(ui._one_line(
    '<table class="cmp"><thead><tr><th>ROC-AUC difference (95% interval)</th>'
    '<th class="num">1 year</th><th class="num">2 years</th>'
    '<th class="num">3 years</th></tr></thead><tbody>'
    + "".join(body) + "</tbody></table>"), unsafe_allow_html=True)
st.markdown(ui.callout(
    "Plain reading: XGBoost is <b>clearly better than logistic regression</b> "
    "at every warning time, and <b>level with random forest and EBM</b> "
    "almost everywhere.",
    "The exceptions are honest ones: at one year random forest is ahead by "
    "about 0.011 ROC-AUC, and at three years XGBoost is slightly ahead of "
    "EBM."), unsafe_allow_html=True)

# --------------------------------------------------------------- why xgb
st.markdown(ui.section(
    "Why XGBoost was chosen",
    "The test results put random forest, EBM and XGBoost in the same top "
    "group, so the choice rests on a mix of accuracy and practical fit, not "
    "on one metric."), unsafe_allow_html=True)

st_look = cu.metric_lookup(data, "static")
gaps = []
for hh in (1, 2, 3):
    top = max(st_look[(m, hh)]["roc"] for m in cu.MODEL_ORDER)
    gaps.append(top - st_look[("xgb", hh)]["roc"])
pr_best = [hh for hh in (1, 2, 3)
           if max(cu.MODEL_ORDER, key=lambda m: st_look[(m, hh)]["pr"]) == "xgb"]
sz = data["size_mb"]
rf_lo, rf_hi = min(sz["rf"]), max(sz["rf"])
xg_lo, xg_hi = min(sz["xgb"]), max(sz["xgb"])
ebm_mb = max(sz["ebm"])
alt_gain = [r for r in data["vs_altman"] if r["model"] == "xgb"
            and r["features"] == "static" and r["metric"] == "ROC_AUC"]
alt1 = [r for r in alt_gain if r["h"] == 1][0]

st.markdown(ui._one_line(f"""
<div class="cards">
<div class="card"><p class="c-h">1. Top group at every warning time</p>
<p class="c-big">within {max(gaps):.3f}</p>
<p>XGBoost's ROC-AUC is never more than {max(gaps):.3f} below the best model
at any horizon, and it has the best PR-AUC at {len(pr_best)} of 3 horizons
({', '.join(str(x) + ' yr' for x in pr_best)}).</p></div>
<div class="card"><p class="c-h">2. Far ahead of the old standard</p>
<p class="c-big">+{alt1['delta']:.3f}</p>
<p>ROC-AUC gain over the Altman Z-score at one year (95% interval
{alt1['lo']:.3f} to {alt1['hi']:.3f}).</p></div>
<div class="card"><p class="c-h">3. Small enough to ship</p>
<p class="c-big">{xg_lo:.2f}-{xg_hi:.2f} MB</p>
<p>Each XGBoost model file, against {rf_lo:.0f}-{rf_hi:.0f} MB for random
forest and {ebm_mb:.0f} MB for EBM. The website carries three models, so
this keeps it light and fast to load.</p></div>
<div class="card"><p class="c-h">4. Exact explanations</p>
<p>The website explains every result with SHAP. For tree models like
XGBoost it can be computed <b>exactly and quickly</b> (TreeSHAP), which is
what powers the "Why this result?" section.</p></div>
<div class="card"><p class="c-h">5. Copes with missing ratios</p>
<p>A ratio is left blank when its denominator is zero or negative.
XGBoost handles blanks natively, while logistic regression and random
forest needed filling in with the median first.</p></div>
<div class="card"><p class="c-h">6. Tuned for rare failures</p>
<p>Trees were added until validation PR-AUC stopped improving
(early stopping), and failures were weighted up. That targets the metric
that matters when failures are rare.</p></div>
</div>"""), unsafe_allow_html=True)

st.markdown(ui.subtitle("Model file size (website models, MB)"),
            unsafe_allow_html=True)
items = [(cu.MODEL_SHORT[m], max(sz[m]), cu.MODEL_COLOR[m],
          "under 0.01" if max(sz[m]) < 0.01 else f"up to {max(sz[m]):.2f}")
         for m in ("logreg", "xgb", "rf", "ebm")]
st.markdown(cu.hbars(items, max(max(sz[m]) for m in sz)),
            unsafe_allow_html=True)

st.markdown(
    '<div class="warn"><p><b>What these results do not show.</b> XGBoost is '
    'not proven better than random forest or EBM; the tests above cannot '
    'separate them. EBM is the most transparent model but trails at two and '
    'three years on PR-AUC. Random forest is a fair alternative if file size '
    'does not matter. A different dataset or period could reorder the top '
    'three.</p></div>', unsafe_allow_html=True)

st.markdown(ui.foot(
    "Numbers come from the project notebooks (Step 4 and Step 6 result "
    "files): test years 2015-2018, 95% intervals from resampling companies. "
    "Altman Z-score is the original 1968 formula, not refitted."),
    unsafe_allow_html=True)
