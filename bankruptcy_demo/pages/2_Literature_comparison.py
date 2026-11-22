"""Our results beside the 25 studies cited in the research paper."""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

import compare_ui as cu
import literature_data as lit
import ui

st.set_page_config(page_title="Compared with earlier studies", layout="wide",
                   initial_sidebar_state="expanded")
ui.inject_css()
cu.inject_extra_css()

data = cu.load_comparison()
look = cu.metric_lookup(data, "static")
x1, a1 = look[("xgb", 1)], look[("altman_z", 1)]
ba = data["balanced_acc"]
healthy_acc = 100 * (1 - x1["pos"] / x1["n"])

st.markdown(ui.masthead(
    "Our results beside 25 earlier studies",
    "The research paper cites 25 studies on bankruptcy and financial "
    "distress prediction. Here is what each reported, our own results, and "
    "an honest read of how they compare."), unsafe_allow_html=True)
try:
    st.page_link("app.py", label="Back to the risk predictor")
except Exception:
    pass

st.markdown(
    '<div class="warn"><p><b>Read this before comparing numbers.</b> The '
    'studies use different countries, years, company types and ways of '
    'scoring. A figure from one study set beside a figure from another is a '
    'rough guide, not a controlled test. Only our own comparison with the '
    'Altman Z-score is run on identical data. Figures for the other studies '
    'are the ones quoted in the paper.</p></div>', unsafe_allow_html=True)

# --------------------------------------------------------------- our results
st.markdown(ui.section(
    "Our results (XGBoost, one year before failure)",
    "Test years 2015-2018, companies the model never trained on in those "
    "years."), unsafe_allow_html=True)
st.markdown(ui._one_line(f"""
<div class="cards">
<div class="card"><p class="c-h">ROC-AUC</p><p class="c-big">{x1['roc']:.3f}</p>
<p>95% interval {x1['roc_lo']:.3f} to {x1['roc_hi']:.3f}</p></div>
<div class="card"><p class="c-h">PR-AUC</p><p class="c-big">{x1['pr']:.3f}</p>
<p>{x1['lift']:.1f} times the base rate of failure</p></div>
<div class="card"><p class="c-h">Failures in the riskiest 10%</p>
<p class="c-big">{cu.pct(x1['rec10'])}</p>
<p>The Altman Z-score finds {cu.pct(a1['rec10'])}</p></div>
<div class="card"><p class="c-h">Balanced accuracy</p>
<p class="c-big">{ba['xgb']:.3f}</p>
<p>Threshold chosen on 2012-2014, then applied to the test years</p></div>
</div>"""), unsafe_allow_html=True)

# ------------------------------------------------- same metric: ROC-AUC
st.markdown(ui.section(
    "The one metric several studies share: ROC-AUC",
    "Dots are the reported value; shaded bands are a range (our 95% "
    "interval, or the study's own range)."), unsafe_allow_html=True)
items = [
    ("Altman Z-score (ours)", a1["roc"], a1["roc_lo"], a1["roc_hi"],
     cu.MODEL_COLOR["altman_z"], f"{a1['roc']:.3f}"),
    ("Logistic regression (ours)", look[("logreg", 1)]["roc"],
     look[("logreg", 1)]["roc_lo"], look[("logreg", 1)]["roc_hi"],
     cu.MODEL_COLOR["logreg"], f"{look[('logreg', 1)]['roc']:.3f}"),
    ("XGBoost (ours)", x1["roc"], x1["roc_lo"], x1["roc_hi"],
     cu.MODEL_COLOR["xgb"], f"{x1['roc']:.3f}"),
    ("[14] Yang and Sun, repeated CV", 0.904, 0.894, 0.914, "#C9A227",
     "0.894 to 0.914"),
    ("[14] Yang and Sun, one split", 0.9286, None, None, "#C9A227", "0.9286"),
    ("[20] Akbarlou and Mastchaman", 0.938, None, None, "#A81F3D", "0.938"),
]
st.markdown(cu.range_chart(items, 0.74, 1.0, [0.75, 0.80, 0.85, 0.90, 0.95,
                                              1.00]), unsafe_allow_html=True)
st.markdown(ui.callout(
    "<b>Straight answer:</b> on this metric our model is <b>in the same "
    "range as the best published results, not above them</b>.",
    "The highest figure, 0.938 in [20], is above our 0.919, although our "
    "interval reaches 0.940 and the two use different data. The dot "
    "for [14] repeated cross-validation sits at the middle of their range "
    "only to anchor the band; they quote a range, not a single value."), unsafe_allow_html=True)

st.markdown(ui.subtitle("Why accuracy figures cannot be set beside ours"),
            unsafe_allow_html=True)
st.markdown(ui._one_line(f"""
<div class="cards">
<div class="card"><p class="c-h">Studies quoting accuracy</p>
<p>[6] 98.46% (on the sample used to fit it), [7] about 87%, [8] 82-83%,
[26] 93% and 99%.</p></div>
<div class="card"><p class="c-h">The accuracy trap</p>
<p class="c-big">{healthy_acc:.1f}%</p>
<p>Accuracy of a model that predicts "nobody fails" on our test years at
one year, because only {x1['pos']} of {x1['n']:,} company-years failed.</p></div>
<div class="card"><p class="c-h">Balanced accuracy, both sides</p>
<p class="c-big">{ba['xgb']:.3f} vs 0.875</p>
<p>Ours against [20]. Theirs is higher, on different data and with a
different threshold.</p></div>
</div>"""), unsafe_allow_html=True)

# ------------------------------------------- where we are on firmer ground
st.markdown(ui.section(
    "Where this project is on firmer ground",
    "Not a higher headline score, but a stricter and wider test. These "
    "points come from our own results, not from the other studies."),
    unsafe_allow_html=True)
alt = [r for r in data["vs_altman"] if r["model"] == "xgb"
       and r["features"] == "static" and r["metric"] == "ROC_AUC"]
alt = {r["h"]: r for r in alt}
st.markdown(ui._one_line(f"""
<div class="cards">
<div class="card"><p class="c-h">Beats the classic score, measured</p>
<p class="c-big">+{alt[1]['delta']:.3f}</p>
<p>ROC-AUC over the Altman Z-score at one year (95% interval
{alt[1]['lo']:.3f} to {alt[1]['hi']:.3f}), and +{alt[3]['delta']:.3f} at three
years. The Z-score's distress zone also flagged 35.3% of companies that
never failed.</p></div>
<div class="card"><p class="c-h">Tested on later years</p>
<p>Trained 1999-2011, scored on 2015-2018. Study [14] shows how much a
score can depend on the evaluation: 0.9286 on one split but 0.894 to 0.914
under repeated cross-validation.</p></div>
<div class="card"><p class="c-h">Five warning times, with intervals</p>
<p class="c-big">0.920 to 0.705</p>
<p>ROC-AUC from one to five years before failure, each with a 95% interval.
Only [18] is described in the paper as covering one to five years.</p></div>
<div class="card"><p class="c-h">Importance is not necessity</p>
<p>SHAP says what the model leans on. Removing each feature group and
retraining shows what it truly needs: only the market-value group
consistently hurt performance.</p></div>
<div class="card"><p class="c-h">Rare-failure metrics</p>
<p>PR-AUC and the share of failures in the riskiest 5% and 10%, rather than
accuracy alone.</p></div>
<div class="card"><p class="c-h">A working demo</p>
<p>Anyone can enter a company's numbers and see the risk and the reasons
behind it, so the model can be tried rather than only read about.</p></div>
</div>"""), unsafe_allow_html=True)
st.markdown(
    '<p class="note">The paper itself says most surveyed studies stress a '
    'headline accuracy or AUC and give less attention to lead time and to '
    'whether top features are truly necessary. That is the paper\'s '
    'reading of the literature, not a result tested here.</p>',
    unsafe_allow_html=True)

# ---------------------------------------------------------- study explorer
st.markdown(ui.section(
    "All 25 studies, one by one",
    "What each reported, taken from the paper, and how it relates to our "
    "results."), unsafe_allow_html=True)

counts = Counter(r["verdict"] for r in lit.ROWS)
segs = "".join(
    f'<div style="flex:{counts[k]};background:{lit.VERDICTS[k][1]}">'
    f'{counts[k]}</div>' for k in lit.VERDICTS if counts[k])
legend = "".join(
    f'<span><i style="background:{lit.VERDICTS[k][1]}"></i>'
    f'{ui.esc(lit.VERDICTS[k][0])} ({counts[k]})</span>'
    for k in lit.VERDICTS if counts[k])
st.markdown(ui._one_line(
    f'<div class="stack">{segs}</div><div class="legend" '
    f'style="border:0;padding:0;margin:0">{legend}</div>'),
    unsafe_allow_html=True)

f1, f2 = st.columns(2)
with f1:
    kinds = st.multiselect("Type of study", lit.KINDS, default=lit.KINDS)
with f2:
    vkeys = st.multiselect(
        "How it relates to ours", list(lit.VERDICTS),
        default=list(lit.VERDICTS),
        format_func=lambda k: lit.VERDICTS[k][0])

shown = [r for r in lit.ROWS if r["kind"] in kinds and r["verdict"] in vkeys]
if not shown:
    st.info("No studies match those filters.")
else:
    body = []
    for r in shown:
        label, color = lit.VERDICTS[r["verdict"]]
        body.append(
            f'<tr><td class="num">[{r["ref"]}]</td>'
            f'<td><b>{ui.esc(r["cite"])}</b><span class="ci">'
            f'{ui.esc(r["kind"])}</span></td>'
            f'<td>{ui.esc(r["setting"])}<span class="ci">'
            f'{ui.esc(r["method"])}</span></td>'
            f'<td>{ui.esc(r["reported"])}</td>'
            f'<td>{cu.badge(label, color)}<span class="ci" '
            f'style="color:#16202E;margin-top:.3rem">'
            f'{ui.esc(r["vs_ours"])}</span></td></tr>')
    st.markdown(ui._one_line(
        '<table class="cmp"><thead><tr><th class="num">Ref</th>'
        '<th>Study</th><th>Data and method</th><th>What it reported</th>'
        '<th>Against our results</th></tr></thead><tbody>'
        + "".join(body) + "</tbody></table>"), unsafe_allow_html=True)
    st.caption(f"Showing {len(shown)} of {len(lit.ROWS)} studies.")

st.markdown(ui.foot(
    "Study details are as summarised in the project's research paper "
    "(literature survey and Table II); numbers for other studies are not "
    "re-checked against the original papers. Our figures come from the "
    "project notebooks. Results are indications, not financial advice."),
    unsafe_allow_html=True)
