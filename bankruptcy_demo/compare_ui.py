"""Shared pieces for the two comparison pages (model comparison and
literature comparison). Pure HTML builders plus a little extra CSS; nothing
here needs Streamlit to import except inject_extra_css().
"""
import json
import os

from ui import _one_line, esc

HERE = os.path.dirname(os.path.abspath(__file__))

MODEL_ORDER = ["altman_z", "logreg", "rf", "xgb", "ebm"]
MODEL_NAME = {"altman_z": "Altman Z-score (1968 formula)",
              "logreg": "Logistic regression", "rf": "Random forest",
              "xgb": "XGBoost", "ebm": "Explainable Boosting Machine"}
MODEL_SHORT = {"altman_z": "Altman Z", "logreg": "Logistic regression",
               "rf": "Random forest", "xgb": "XGBoost", "ebm": "EBM"}
MODEL_COLOR = {"altman_z": "#8E9BA9", "logreg": "#C9A227", "rf": "#3A9B7A",
               "xgb": "#0F4C5C", "ebm": "#C8452F"}

EXTRA_CSS = """
<style>
.cmp{width:100%;border-collapse:collapse;background:var(--surface);
border:1px solid var(--line);border-radius:8px;overflow:hidden;font-size:.93rem;}
.cmp th{background:#EDF1F5;text-align:left;font-weight:600;padding:.6rem .8rem;
color:var(--ink);border-bottom:1px solid var(--line);}
.cmp td{padding:.6rem .8rem;border-top:1px solid var(--line);vertical-align:top;}
.cmp td.num,.cmp th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;}
.cmp tr.pick td{background:#E6F1F3;}
.cmp .best{font-weight:700;color:var(--brand);}
.cmp .ci{display:block;color:var(--muted);font-size:.78rem;font-weight:400;}
.dot{display:inline-block;width:.7rem;height:.7rem;border-radius:50%;margin-right:.45rem;}
.badge{display:inline-block;padding:.12rem .55rem;border-radius:999px;font-size:.78rem;
font-weight:600;color:#fff;white-space:nowrap;}
.note{color:var(--muted);font-size:.86rem;margin:.5rem 0 0;max-width:80ch;}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(15.5rem,1fr));gap:1rem;margin:.6rem 0;}
.card{background:var(--surface);border:1px solid var(--line);border-top:4px solid var(--brand);
border-radius:8px;padding:1rem 1.1rem;}
.card .c-h{font-weight:700;margin:0 0 .3rem;font-family:'Bricolage Grotesque',sans-serif;font-size:1.05rem;}
.card p{margin:.2rem 0;font-size:.93rem;}
.card .c-big{font-family:'Bricolage Grotesque',sans-serif;font-size:1.7rem;font-weight:700;color:var(--brand);margin:.1rem 0;}
.warn{background:#FFF7E6;border:1px solid #F0D9A8;border-left:4px solid #C9A227;border-radius:6px;
padding:.9rem 1.2rem;margin:.8rem 0;}
.warn p{margin:.2rem 0;}
.hbar{display:grid;grid-template-columns:11rem 1fr 6.5rem;gap:.8rem;align-items:center;margin:.45rem 0;}
.hb-track{background:#E9EDF2;height:16px;border-radius:3px;position:relative;}
.hb-fill{position:absolute;left:0;top:0;bottom:0;border-radius:3px;}
.hb-val{font-variant-numeric:tabular-nums;font-size:.9rem;text-align:right;}
.axis{position:relative;height:2.6rem;margin:.2rem 0 0 12.3rem;}
.rng{display:grid;grid-template-columns:11.5rem 1fr;gap:.8rem;align-items:center;margin:.55rem 0;}
.rng-track{position:relative;height:1.5rem;background:linear-gradient(#E9EDF2,#E9EDF2) center/100% 2px no-repeat;}
.rng-band{position:absolute;top:.45rem;height:.6rem;border-radius:3px;opacity:.45;}
.rng-dot{position:absolute;top:.25rem;width:1rem;height:1rem;border-radius:50%;transform:translateX(-50%);
border:2px solid #fff;box-shadow:0 0 0 1px rgba(22,32,46,.4);}
.rng-lab{position:absolute;top:-.05rem;font-size:.76rem;color:var(--ink);transform:translateX(8px);white-space:nowrap;}
.tick{position:absolute;top:0;font-size:.74rem;color:var(--muted);transform:translateX(-50%);}
.tick-line{position:absolute;top:1rem;bottom:0;width:1px;background:#C5CED8;}
@media (max-width:760px){
.hbar,.rng{grid-template-columns:1fr;gap:.2rem;}
.axis{margin-left:0;}
.cmp{font-size:.85rem;}
}
</style>
"""


def inject_extra_css():
    import streamlit as st
    css = "\n".join(l for l in EXTRA_CSS.splitlines() if l.strip())
    st.markdown(css, unsafe_allow_html=True)


def load_comparison():
    with open(os.path.join(HERE, "assets", "model_comparison.json")) as fh:
        return json.load(fh)


def metric_lookup(data, features="static"):
    """{(model, h): row} for the chosen feature set (Altman has no set)."""
    out = {}
    for r in data["metrics"]:
        if r["model"] == "altman_z" or r["features"] == features:
            out[(r["model"], r["h"])] = r
    return out


def f3(x):
    return f"{x:.3f}"


def pct(x):
    return f"{100 * x:.1f}%"


def dot(model):
    return f'<span class="dot" style="background:{MODEL_COLOR[model]}"></span>'


def badge(text, color):
    return f'<span class="badge" style="background:{color}">{esc(text)}</span>'


def score_table(rows_by_model, best, pick="xgb"):
    """Scoreboard: one row per model. `best` maps a column key to the set of models
    that win it (ties allowed); the picked model's row is shaded."""
    head = ("<tr><th>Model</th><th class=\"num\">ROC-AUC</th>"
            "<th class=\"num\">PR-AUC</th>"
            "<th class=\"num\">Failures caught in riskiest 10%</th>"
            "<th class=\"num\">Failures caught in riskiest 5%</th></tr>")
    body = []
    for m in MODEL_ORDER:
        r = rows_by_model[m]

        def cell(key, text, ci=""):
            cls = "num best" if m in best[key] else "num"
            sub = f'<span class="ci">{ci}</span>' if ci else ""
            return f'<td class="{cls}">{text}{sub}</td>'

        tr = ' class="pick"' if m == pick else ""
        body.append(
            f"<tr{tr}><td>{dot(m)}{esc(MODEL_NAME[m])}</td>"
            + cell("roc", f3(r["roc"]),
                   f'95% CI {f3(r["roc_lo"])} to {f3(r["roc_hi"])}')
            + cell("pr", f3(r["pr"]),
                   f'{r["lift"]:.1f}x the base rate')
            + cell("rec10", pct(r["rec10"]))
            + cell("rec5", pct(r["rec5"])) + "</tr>")
    return _one_line(f'<table class="cmp"><thead>{head}</thead>'
                     f'<tbody>{"".join(body)}</tbody></table>')


def hbars(items, vmax, fmt="{:.2f}", note=""):
    """items: [(label, value, color, shown_text or None)]."""
    out = []
    for label, v, color, shown in items:
        w = max(0.0, min(100.0, 100.0 * v / vmax))
        out.append(
            f'<div class="hbar"><div>{esc(label)}</div><div class="hb-track">'
            f'<div class="hb-fill" style="width:{w}%;background:{color}"></div>'
            f'</div><div class="hb-val">{esc(shown or fmt.format(v))}</div></div>')
    return _one_line("".join(out))


def range_chart(items, lo, hi, ticks):
    """Dot-and-band chart on a shared axis.
    items: [(label, point, band_lo, band_hi, color, text)]."""
    span = hi - lo

    def x(v):
        return 100.0 * (min(max(v, lo), hi) - lo) / span

    tick_html = "".join(
        f'<span class="tick" style="left:{x(t)}%">{t:.2f}</span>'
        f'<span class="tick-line" style="left:{x(t)}%"></span>' for t in ticks)
    rows = []
    for label, p, a, b, color, text in items:
        band = ""
        if a is not None and b is not None:
            band = (f'<span class="rng-band" style="left:{x(a)}%;'
                    f'width:{max(x(b) - x(a), 0.6)}%;background:{color}"></span>')
        rows.append(
            f'<div class="rng"><div>{esc(label)}</div><div class="rng-track">'
            f'{band}<span class="rng-dot" style="left:{x(p)}%;'
            f'background:{color}"></span>'
            f'<span class="rng-lab" style="left:{x(p)}%">{esc(text)}</span>'
            f'</div></div>')
    return _one_line(f'<div class="axis">{tick_html}</div>' + "".join(rows))
