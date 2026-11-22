"""Look and feel for the demo: stylesheet plus small HTML components.

Nothing here needs Streamlit to import (inject_css imports it lazily), so the
helpers can be tested on their own. All user-supplied text goes through esc().
"""
import html
import re

TIER_ORDER = ["Low", "Moderate", "Elevated", "High", "Very high"]
TIER_COLOR = {"Low": "#3A9B7A", "Moderate": "#C9A227", "Elevated": "#E08A1E",
              "High": "#D2543A", "Very high": "#A81F3D"}
# percentile band of each tier (matches scoring.TIERS)
ZONES = [(0, 80, "Low"), (80, 90, "Moderate"), (90, 95, "Elevated"),
         (95, 98, "High"), (98, 100, "Very high")]
TIER_MEANING = {"Low": "lower 80%", "Moderate": "top 20%",
                "Elevated": "top 10%", "High": "top 5%",
                "Very high": "top 2%"}
UP, DOWN = "#C8452F", "#1F7A8C"


def esc(x):
    return html.escape(str(x), quote=True)


def _one_line(s):
    """Collapse a template to one line: Markdown treats indented or blank
    lines inside HTML as code blocks, so none may survive."""
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


def hz(h):
    return f"{h} year" + ("s" if h > 1 else "")


def fmt_num(v):
    if v is None:
        return "not provided"
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:.2f}"


def outcome_text(note):
    """Turn the sample-file note into a sentence about what really happened."""
    m = re.match(r"failed (\d) year", str(note))
    if m:
        n = int(m.group(1))
        return (f"This company went bankrupt {n} year"
                + ("s" if n > 1 else "") + " after this report.")
    if str(note) == "never failed":
        return "This company did not fail during the period covered by the data."
    return ""


# --------------------------------------------------------------------- CSS
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Public+Sans:wght@400;500;600&display=swap');
:root{--paper:#F4F6F8;--surface:#FFFFFF;--ink:#16202E;--muted:#586474;
--line:#DCE2E9;--brand:#0F4C5C;--up:#C8452F;--down:#1F7A8C;}
.stApp{background:var(--paper);}
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea,
.stApp button, .stApp th, .stApp td{font-family:'Public Sans',system-ui,-apple-system,'Segoe UI',sans-serif;}
.stApp p, .stApp li{line-height:1.6;}
.stApp h1,.stApp h2,.stApp h3,.hero-title,.sec-title,.v-title,.sub-title{
font-family:'Bricolage Grotesque','Public Sans',system-ui,sans-serif;
letter-spacing:-0.015em;color:var(--ink);}
.block-container,[data-testid="stMainBlockContainer"]{max-width:1040px;padding:2.2rem 2rem 4rem;}
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none;visibility:hidden;}
[data-testid="stHeader"]{background:transparent;}
[data-testid="stSidebar"]{background:var(--surface);border-right:1px solid var(--line);}
[data-testid="stSidebar"] .block-container,[data-testid="stSidebarUserContent"]{padding-top:1.4rem;}
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"]>button{
border-radius:6px;font-weight:600;}
[data-testid="stForm"]{border:0;padding:0;}
:focus-visible{outline:3px solid #6FB3C2;outline-offset:2px;}

.brand{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;color:var(--brand);
font-size:1rem;letter-spacing:-0.005em;margin-bottom:1.6rem;display:flex;align-items:center;gap:.55rem;}
.brand svg{display:block;}
.hero-title{font-size:2.55rem;line-height:1.08;font-weight:700;margin:0 0 .8rem;max-width:22ch;}
.hero-sub{font-size:1.08rem;color:var(--muted);max-width:60ch;margin:0 0 .4rem;}
.side-title{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:1.25rem;margin:0 0 .15rem;}
.side-note{color:var(--muted);font-size:.88rem;margin:0 0 .8rem;}
.mini{font-weight:600;font-size:.92rem;margin:1rem 0 .1rem;color:var(--ink);}

.sec-title{font-size:1.55rem;font-weight:700;margin:2.6rem 0 .3rem;}
.sec-lead{color:var(--muted);max-width:68ch;margin:0 0 1rem;}
.sub-title{font-size:1.1rem;font-weight:700;margin:1.8rem 0 .5rem;}

/* verdict */
.verdict{background:var(--surface);border:1px solid var(--line);border-left-width:6px;
border-radius:8px;padding:1.4rem 1.6rem 1.1rem;margin-top:.8rem;}
.v-name{color:var(--muted);font-size:.92rem;margin:0;}
.v-title{font-size:2rem;line-height:1.15;font-weight:700;margin:.25rem 0 .4rem;}
.v-sub{color:var(--muted);margin:0 0 1.1rem;max-width:64ch;}
.r-row{display:grid;grid-template-columns:4.6rem 1fr 11.5rem;gap:1rem;align-items:center;margin:.85rem 0;}
.r-label{font-weight:600;}
.track{position:relative;height:14px;border-radius:3px;background:#E9EDF2;}
.zone{position:absolute;top:0;bottom:0;}
.mark{position:absolute;top:-6px;width:8px;height:26px;border-radius:2px;
transform:translateX(-50%);border:2px solid #fff;box-shadow:0 0 0 1px rgba(22,32,46,.35);}
.r-tier{font-weight:600;line-height:1.2;}
.r-sub{color:var(--muted);font-size:.82rem;}
.legend{display:flex;flex-wrap:wrap;gap:.35rem 1.1rem;margin:1.1rem 0 0;padding-top:.9rem;
border-top:1px solid var(--line);font-size:.84rem;color:var(--muted);}
.legend span{display:inline-flex;align-items:center;gap:.4rem;}
.legend i{width:.8rem;height:.8rem;border-radius:2px;display:inline-block;}
.v-foot{margin:.9rem 0 0;font-size:.92rem;color:var(--ink);}
.v-foot p{margin:.15rem 0;}

/* explanation */
.callout{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--brand);
border-radius:6px;padding:1rem 1.3rem;margin:.6rem 0 0;}
.callout p{margin:.2rem 0;}
.c-main{font-size:1.05rem;}
.c-sub{color:var(--muted);}
.g-head,.g-row{display:grid;grid-template-columns:12rem 1fr 7.5rem;gap:.9rem;align-items:center;}
.g-head{color:var(--muted);font-size:.82rem;margin-top:.3rem;}
.g-head .l{text-align:right;padding-right:.4rem;}
.g-head .r{padding-left:.4rem;}
.g-head .mid{display:grid;grid-template-columns:1fr 1fr;}
.g-row{margin:.35rem 0;}
.g-name{font-weight:500;}
.g-track{position:relative;height:18px;}
.g-axis{position:absolute;left:50%;top:-4px;bottom:-4px;width:1px;background:#8E9BA9;}
.g-bar{position:absolute;top:2px;bottom:2px;border-radius:2px;}
.g-dir{color:var(--muted);font-size:.84rem;}
.key{display:flex;flex-wrap:wrap;gap:.3rem 1.2rem;color:var(--muted);font-size:.85rem;margin:.2rem 0 .6rem;}
.key span{display:inline-flex;align-items:center;gap:.4rem;}
.k-band{width:1.4rem;height:.6rem;background:#CFE4E9;border-radius:2px;display:inline-block;}
.k-dot{width:.7rem;height:.7rem;border-radius:50%;background:var(--ink);display:inline-block;}
.k-med{width:2px;height:.8rem;background:#6B7A8A;display:inline-block;}

.factor{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:1.6rem;
padding:1rem 0 1rem 1.1rem;border-top:1px solid var(--line);border-left:3px solid var(--up);margin-left:0;}
.factor.down{border-left-color:var(--down);}
.f-top{display:flex;flex-wrap:wrap;align-items:baseline;gap:.2rem .7rem;}
.f-name{font-weight:600;font-size:1.02rem;}
.f-tag{color:var(--muted);font-size:.82rem;}
.f-text{margin:.25rem 0 .15rem;}
.f-num{margin:0;color:var(--muted);font-size:.9rem;}
.strip{position:relative;height:3.2rem;margin-top:.5rem;}
.s-track{position:absolute;left:0;right:0;top:.95rem;height:2px;background:#C5CED8;}
.s-band{position:absolute;top:.65rem;height:.65rem;background:#CFE4E9;border-radius:2px;}
.s-med{position:absolute;top:.55rem;height:.85rem;width:2px;background:#6B7A8A;}
.s-me{position:absolute;top:.4rem;width:1rem;height:1rem;border-radius:50%;
transform:translateX(-50%);border:2px solid #fff;box-shadow:0 0 0 1px rgba(22,32,46,.4);}
.s-me.off{border-radius:3px;}
.s-lab{position:absolute;top:1.7rem;font-size:.74rem;color:var(--muted);transform:translateX(-50%);white-space:nowrap;}
.s-you{position:absolute;top:-.55rem;font-size:.74rem;font-weight:600;transform:translateX(-50%);white-space:nowrap;}

.stack{display:flex;height:2.4rem;border-radius:6px;overflow:hidden;margin:.5rem 0 .6rem;}
.stack div{display:flex;align-items:center;justify-content:center;color:#fff;font-weight:600;font-size:.9rem;min-width:0;}
.foot{color:var(--muted);font-size:.86rem;margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);max-width:80ch;}

@media (max-width:760px){
.hero-title{font-size:2rem;}
.r-row{grid-template-columns:1fr;gap:.35rem;}
.g-head,.g-row{grid-template-columns:1fr;gap:.2rem;}
.g-head{display:none;}
.factor{grid-template-columns:1fr;gap:.4rem;}
.v-title{font-size:1.6rem;}
.block-container,[data-testid="stMainBlockContainer"]{padding:1.2rem 1rem 3rem;}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important;}}
</style>
"""


def inject_css():
    import streamlit as st
    css = "\n".join(l for l in CSS.splitlines() if l.strip())
    st.markdown(css, unsafe_allow_html=True)


# --------------------------------------------------------------- components
def masthead(title, sub):
    logo = ('<svg width="22" height="22" viewBox="0 0 22 22" aria-hidden="true">'
            '<rect x="2" y="12" width="4" height="8" rx="1" fill="#3A9B7A"/>'
            '<rect x="9" y="7" width="4" height="13" rx="1" fill="#E08A1E"/>'
            '<rect x="16" y="2" width="4" height="18" rx="1" fill="#A81F3D"/></svg>')
    return _one_line(f"""
    <div class="brand">{logo}<span>Distress early warning</span></div>
    <div class="hero-title">{esc(title)}</div>
    <p class="hero-sub">{esc(sub)}</p>""")


def section(title, lead=None):
    out = f'<div class="sec-title">{esc(title)}</div>'
    if lead:
        out += f'<p class="sec-lead">{lead}</p>'
    return _one_line(out)


def subtitle(text):
    return f'<div class="sub-title">{esc(text)}</div>'


def _ruler(pct):
    p = min(max(float(pct), 0.8), 99.2)
    tier = tier_for(pct)
    zones = "".join(
        f'<span class="zone" style="left:{a}%;width:{b - a}%;'
        f'background:{TIER_COLOR[t]}55"></span>' for a, b, t in ZONES)
    return (f'<div class="track">{zones}<span class="mark" '
            f'style="left:{p}%;background:{TIER_COLOR[tier]}"></span></div>')


def tier_for(pct):
    for a, b, t in reversed(ZONES):
        if pct >= a:
            return t
    return "Low"


def verdict(name, rows, z, zone, n_test, truth_note=None):
    """rows: [{"h":1,"tier":..,"pct":..}, ...] for the three horizons."""
    first = rows[0]
    color = TIER_COLOR[first["tier"]]
    body = ""
    for r in rows:
        c = TIER_COLOR[r["tier"]]
        body += (f'<div class="r-row"><div class="r-label">{hz(r["h"])}</div>'
                 f'{_ruler(r["pct"])}'
                 f'<div><div class="r-tier" style="color:{c}">{r["tier"]} risk</div>'
                 f'<div class="r-sub">riskier than {r["pct"]:.0f}% of test cases</div>'
                 f'</div></div>')
    legend = "".join(
        f'<span><i style="background:{TIER_COLOR[t]}"></i>{t}: {TIER_MEANING[t]}</span>'
        for t in TIER_ORDER[::-1])
    zname = zone.split(" (")[0].lower() if zone and zone != "n/a" else None
    altman = (f"Classic Altman Z-score (1968): {z:.2f}, {zname}."
              if zname and z == z else "Classic Altman Z-score: not available.")
    foot = f"<p>{esc(altman)}</p>"
    out = outcome_text(truth_note) if truth_note else ""
    if out:
        foot += f"<p><b>What really happened:</b> {esc(out)}</p>"
    return _one_line(f"""
    <div class="verdict" style="border-left-color:{color}">
      <p class="v-name">{esc(name)}</p>
      <div class="v-title">{first["tier"]} risk of failing within a year</div>
      <p class="v-sub">Further right on the bars means riskier. Each bar ranks this
      company against {n_test:,} company-years from 2015 to 2018 that the model
      had never seen.</p>
      {body}
      <div class="legend">{legend}</div>
      <div class="v-foot">{foot}</div>
    </div>""")


def tier_stack(counts):
    """counts: {tier: n}. Left = safest, right = riskiest."""
    total = sum(counts.values()) or 1
    segs = "".join(
        f'<div style="flex:{counts[t]};background:{TIER_COLOR[t]}" '
        f'title="{t}: {counts[t]}">{counts[t] if counts[t] / total > .06 else ""}</div>'
        for t in TIER_ORDER if counts.get(t, 0) > 0)
    legend = "".join(
        f'<span><i style="background:{TIER_COLOR[t]}"></i>{t}: {counts.get(t, 0)}</span>'
        for t in TIER_ORDER)
    return _one_line(f'<div class="stack">{segs}</div><div class="legend" '
                     f'style="border:0;padding:0;margin:0">{legend}</div>')


def callout(main_html, sub_html=""):
    sub = f'<p class="c-sub">{sub_html}</p>' if sub_html else ""
    return _one_line(f'<div class="callout"><p class="c-main">{main_html}</p>{sub}</div>')


def _join_names(items):
    names = [f"<b>{esc(x['label'])}</b>" for x in items]
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


def summary_sentence(raising, lowering):
    parts = []
    if raising:
        parts.append("The result is pushed up mainly by "
                     f"{_join_names(raising[:3])}.")
    if lowering:
        parts.append(f"It is held down by {_join_names(lowering[:2])}.")
    return " ".join(parts) or "No single number stands out for this company."


def group_bars(groups):
    """groups: [(name, effect)] -> diverging bars around a centre line."""
    big = max((abs(v) for _, v in groups), default=0) or 1.0
    rows = ""
    for name, v in sorted(groups, key=lambda t: t[1]):
        w = abs(v) / big * 50
        if abs(v) < 0.04 * big:
            bar, label = "", "about neutral"
        elif v > 0:
            bar = (f'<span class="g-bar" style="left:50%;width:{w:.1f}%;'
                   f'background:{UP}"></span>')
            label = "raises risk"
        else:
            bar = (f'<span class="g-bar" style="left:{50 - w:.1f}%;width:{w:.1f}%;'
                   f'background:{DOWN}"></span>')
            label = "lowers risk"
        rows += (f'<div class="g-row"><div class="g-name">{esc(name)}</div>'
                 f'<div class="g-track"><span class="g-axis"></span>{bar}</div>'
                 f'<div class="g-dir">{label}</div></div>')
    head = ('<div class="g-head"><div></div><div class="mid">'
            '<div class="l">lowers risk</div><div class="r">raises risk</div>'
            '</div><div></div></div>')
    return _one_line(head + rows)


def range_key():
    return _one_line("""
    <div class="key">
      <span><i class="k-band"></i>where most healthy companies sit</span>
      <span><i class="k-med"></i>typical healthy company</span>
      <span><i class="k-dot"></i>this company</span>
    </div>""")


def _strip(f, color):
    lo, hi, med, v = f["lo"], f["hi"], f["median"], f["value"]
    span = (hi - lo) or 1.0
    a, b = lo - 0.7 * span, hi + 0.7 * span

    def pos(x):
        return (x - a) / (b - a) * 100

    band_l, band_r = pos(lo), pos(hi)
    out = ('<div class="strip"><span class="s-track"></span>'
           f'<span class="s-band" style="left:{band_l:.1f}%;'
           f'width:{band_r - band_l:.1f}%"></span>'
           f'<span class="s-med" style="left:{pos(med):.1f}%"></span>')
    if v is not None:
        p = min(max(pos(v), 3), 97)
        off = " off" if pos(v) < 3 or pos(v) > 97 else ""
        out += (f'<span class="s-me{off}" style="left:{p:.1f}%;background:{color}">'
                f'</span><span class="s-you" style="left:{p:.1f}%;color:{color}">'
                f'{esc(fmt_num(v))}</span>')
    out += (f'<span class="s-lab" style="left:{band_l:.1f}%">{esc(fmt_num(lo))}</span>'
            f'<span class="s-lab" style="left:{band_r:.1f}%">{esc(fmt_num(hi))}</span>'
            '</div>')
    return out


def factors(items, kind):
    """kind: 'up' (raises risk) or 'down' (lowers risk)."""
    if not items:
        return '<p class="sec-lead">Nothing notable.</p>'
    color = UP if kind == "up" else DOWN
    out = ""
    for f in items:
        v = f["value"]
        if v is None:
            num = "This value was not provided."
        else:
            num = (f"Value: {fmt_num(v)}. Most healthy companies are between "
                   f"{fmt_num(f['lo'])} and {fmt_num(f['hi'])}.")
        tag = f"{f['strength']} factor, {f['share'] * 100:.0f}% of the model's total influence"
        out += (f'<div class="factor {"down" if kind == "down" else ""}">'
                f'<div><div class="f-top"><span class="f-name">{esc(f["label"])}</span>'
                f'<span class="f-tag">{esc(tag)}</span></div>'
                f'<p class="f-text">{esc(f["why"])}</p>'
                f'<p class="f-num">{esc(num)}</p></div>'
                f'<div>{_strip(f, color)}</div></div>')
    return out


def foot(text):
    return f'<div class="foot">{esc(text)}</div>'
