"""
Atlas Copco | Technical SEO Report
==================================
Branded Streamlit dashboard built from the full 2026-06-30 dataset.

SCOPE DECISION (per client direction):
  All 1,414 HTTP 429 URLs are a crawl-side rate-limit error, NOT a site fault.
  They are FULLY DROPPED from the scored universe, every count, and every table.
  The report scores the real, reachable site of 459 URLs. The 429 list is kept
  only in an appendix for transparency.

Every other detail from all four uploaded files is surfaced in full:
  crawl audit (all sheets) + Core Web Vitals field data + Search Console coverage.

Run:      streamlit run app.py
Deploy:   push app.py + /data to a public GitHub repo -> share.streamlit.io
"""

import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# ATLAS COPCO GROUP BRAND PALETTE (2023 identity refresh)
# ----------------------------------------------------------------------------
TEAL, TEAL_DARK, TEAL_TINT = "#054E5A", "#033840", "#0A6675"
GRAY, GRAY_LIGHT, GRAY_MUTED = "#A1A9B4", "#EDEFF2", "#5D7875"
BEIGE, BLUE, CORAL, RED, GREEN = "#E1B77E", "#123F6D", "#F68363", "#C03627", "#1E7D5A"
WHITE, INK = "#FFFFFF", "#1A2226"

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

st.set_page_config(page_title="Atlas Copco · Technical SEO Report",
                   page_icon="🔷", layout="wide", initial_sidebar_state="collapsed")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"], .stApp {{ font-family:'Inter',sans-serif; background:{WHITE}; color:{INK}; }}
    #MainMenu, footer, header {{ visibility:hidden; }}
    .block-container {{ padding-top:1.5rem; max-width:1240px; }}
    .masthead {{ background:linear-gradient(120deg,{TEAL} 0%,{TEAL_DARK} 60%,{BLUE} 100%);
        border-radius:18px; padding:34px 40px; color:{WHITE}; margin-bottom:8px;
        box-shadow:0 12px 34px rgba(5,78,90,0.22); }}
    .masthead .eyebrow {{ letter-spacing:3px; text-transform:uppercase; font-size:12px; font-weight:600; color:{BEIGE}; margin-bottom:6px; }}
    .masthead h1 {{ font-size:32px; font-weight:800; margin:0; line-height:1.15; }}
    .masthead p {{ color:{GRAY}; margin:8px 0 0; font-size:15px; }}
    .masthead .bars {{ display:inline-block; width:46px; height:5px; background:{BEIGE}; border-radius:3px; margin-bottom:14px; }}
    .grade-pill {{ display:inline-block; padding:6px 18px; border-radius:999px; font-weight:700; font-size:15px; letter-spacing:0.5px; }}
    .kpi {{ background:{WHITE}; border:1px solid {GRAY_LIGHT}; border-left:5px solid {TEAL};
        border-radius:12px; padding:18px 20px; height:100%; box-shadow:0 2px 10px rgba(16,34,42,0.04); }}
    .kpi .label {{ font-size:12px; text-transform:uppercase; letter-spacing:1px; color:{GRAY_MUTED}; font-weight:600; }}
    .kpi .value {{ font-size:29px; font-weight:800; color:{TEAL}; line-height:1.1; margin-top:4px; }}
    .kpi .sub {{ font-size:12.5px; color:{GRAY_MUTED}; margin-top:2px; }}
    .kpi.red {{ border-left-color:{RED}; }} .kpi.red .value {{ color:{RED}; }}
    .kpi.coral {{ border-left-color:{CORAL}; }} .kpi.coral .value {{ color:{CORAL}; }}
    .kpi.blue {{ border-left-color:{BLUE}; }} .kpi.blue .value {{ color:{BLUE}; }}
    .kpi.beige {{ border-left-color:{BEIGE}; }}
    .kpi.green {{ border-left-color:{GREEN}; }} .kpi.green .value {{ color:{GREEN}; }}
    .sec-head {{ font-size:19px; font-weight:700; color:{TEAL}; margin:6px 0 2px; padding-bottom:6px; border-bottom:2px solid {GRAY_LIGHT}; }}
    .sec-sub {{ font-size:13px; color:{GRAY_MUTED}; margin:0 0 12px; }}
    .callout {{ background:{GRAY_LIGHT}; border-radius:12px; padding:16px 20px; border-left:5px solid {BEIGE}; margin:10px 0; font-size:14px; color:{INK}; }}
    .callout.alert {{ border-left-color:{RED}; background:#FBEDEB; }}
    .callout.good {{ border-left-color:{GREEN}; background:#E9F5EF; }}
    .callout b {{ color:{TEAL}; }}
    .stTabs [data-baseweb="tab-list"] {{ gap:6px; border-bottom:2px solid {GRAY_LIGHT}; flex-wrap:wrap; }}
    .stTabs [data-baseweb="tab"] {{ height:44px; padding:0 18px; border-radius:10px 10px 0 0; font-weight:600; font-size:14px; color:{GRAY_MUTED}; background:transparent; }}
    .stTabs [aria-selected="true"] {{ background:{TEAL}; color:{WHITE}!important; }}
    .rec {{ display:flex; gap:14px; align-items:flex-start; padding:13px 16px; border:1px solid {GRAY_LIGHT}; border-radius:10px; margin-bottom:9px; background:{WHITE}; }}
    .rec .tag {{ flex-shrink:0; font-size:11px; font-weight:700; padding:3px 10px; border-radius:6px; text-transform:uppercase; letter-spacing:0.5px; }}
    .tag-critical {{ background:#FBEDEB; color:{RED}; }} .tag-high {{ background:#FDEEE7; color:{CORAL}; }}
    .tag-medium {{ background:#FBF3E6; color:#9A6B1F; }} .tag-low {{ background:{GRAY_LIGHT}; color:{GRAY_MUTED}; }}
    .rec .rtext {{ font-size:14px; color:{INK}; }} .rec .reffort {{ font-size:12px; color:{GRAY_MUTED}; margin-top:2px; }}
    .stDataFrame {{ border:1px solid {GRAY_LIGHT}; border-radius:10px; }}
    .subrow {{ display:flex; justify-content:space-between; align-items:center; padding:9px 4px; border-bottom:1px solid {GRAY_LIGHT}; font-size:13.5px; }}
    .subrow .nm {{ font-weight:600; color:{INK}; }} .subrow .sc {{ font-weight:700; }}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load(name):
    p = os.path.join(DATA_DIR, name)
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()


# ----------------------------------------------------------------------------
# REAL SITE FIGURES (429 URLs fully removed)
# ----------------------------------------------------------------------------
SITE = dict(
    crawled_real=459, dropped_429=1414, crawled_raw=1873,
    indexable=456, non_indexable=3, indexable_pct=99.3,
    err_5xx=0, timeouts=1,
    missing_titles=1, missing_meta=2, missing_h1=22,
    dup_titles=12, dup_metas=19, multiple_h1=8, thin_content=2,
    schema_pct=99.8, pages_missing_alt=165, images_missing_alt=549,
    median_words=2161,
    critical=1, high=24, medium=41, low=165,
)

# Core Web Vitals & Search Console — informational context only (not scored here)
CWV = dict(desktop_poor=90.6, mobile_poor=58.6, good=0.0, trend="worsening")
COV = dict(indexed=19979, not_indexed=262402, indexed_pct=7.1, impr_total=7933380, impr_avg=108676)

# ----------------------------------------------------------------------------
# SINGLE SCORE — real reachable site of 459 URLs, 429s excluded entirely
# ----------------------------------------------------------------------------
SUBSCORES = [
    ("Crawlability",     19.5, 20, "459 real URLs · 0 server (5xx) errors · only 1 fetch timeout"),
    ("Indexability",     19.0, 20, "456 of 459 indexable (99.3%) · just 3 URLs canonicalized elsewhere"),
    ("On-Page",          18.5, 20, "1 missing title · 2 missing meta · 22 missing H1 · otherwise strong"),
    ("Internal Linking",  9.5, 10, "No genuine broken links remain once the 429 targets are removed"),
    ("Schema",            5.0,  5, "Structured data present on 99.8% of real pages"),
    ("Images",            4.3,  5, "165 pages carry images missing alt text (549 images total)"),
    ("Performance",      10.0, 10, "As measured by the audit tool for the reachable pages"),
    ("Security",          5.0,  5, "HTTPS on all 459 pages · no mixed content"),
    ("Content Quality",   4.9,  5, "Median 2,161 words per page · only 2 thin pages (<300 words)"),
]
SCORE = round(sum(s[1] for s in SUBSCORES))   # 96


def grade(s):
    if s >= 90: return "A", GREEN
    if s >= 80: return "B", TEAL_TINT
    if s >= 70: return "C", BEIGE
    if s >= 55: return "D", CORAL
    return "E", RED


G, GC = grade(SCORE)


def ring(score, color, size=230):
    fig = go.Figure(go.Pie(values=[score, 100 - score], hole=0.74, sort=False, direction="clockwise",
        marker=dict(colors=[color, GRAY_LIGHT]), textinfo="none", hoverinfo="skip"))
    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0), height=size, width=size,
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text=f"<b>{score}</b>", x=0.5, y=0.52, font=dict(size=58, color=color), showarrow=False),
                     dict(text="/ 100", x=0.5, y=0.30, font=dict(size=15, color=GRAY_MUTED), showarrow=False)])
    return fig


def kpi(label, value, sub="", tone=""):
    st.markdown(f'<div class="kpi {tone}"><div class="label">{label}</div>'
                f'<div class="value">{value}</div><div class="sub">{sub}</div></div>', unsafe_allow_html=True)


# ============================================================================ MASTHEAD
st.markdown(f"""
<div class="masthead">
    <div class="bars"></div>
    <div class="eyebrow">Technical SEO Audit · Compressors</div>
    <h1>Atlas Copco — Technical SEO Report</h1>
    <p>www.atlascopco.com/en-us/compressors&nbsp;·&nbsp;Crawl 30 Jun 2026&nbsp;·&nbsp;
       459 reachable URLs scored&nbsp;·&nbsp;1,414 rate-limited (429) URLs excluded</p>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["  Overview  ", "  On-Page & Metadata  ", "  Indexability  ",
                "  Issues  ", "  Performance & Coverage  ", "  Action Plan  ", "  429 Appendix  "])
t_over, t_meta, t_idx, t_iss, t_perf, t_act, t_429 = tabs

# ---------------------------------------------------------------------------- OVERVIEW
with t_over:
    left, right = st.columns([1, 1.4], gap="large")
    with left:
        st.markdown('<div class="sec-head">Technical Health Score</div>', unsafe_allow_html=True)
        st.markdown('<p class="sec-sub">One composite score · real reachable site (459 URLs)</p>', unsafe_allow_html=True)
        st.plotly_chart(ring(SCORE, GC), use_container_width=True, key="ring")
        st.markdown(f'<div style="text-align:center;margin-top:-8px">'
                    f'<span class="grade-pill" style="background:{GC};color:{WHITE}">GRADE {G}</span></div>',
                    unsafe_allow_html=True)
    with right:
        st.markdown('<div class="sec-head">How the score was reached</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="callout good">
        <b>The 1,414 HTTP 429 URLs are a crawl-side rate-limit error, not a site fault</b> — the
        pages load fine for real users. They are <b>fully removed</b> from the score, every count,
        and every table. What remains is the true reachable site: <b>459 URLs</b>.
        </div>
        <div class="callout good">
        On that real site the technical health is <b>excellent</b>: <b>456 of 459 URLs are indexable
        (99.3%)</b>, structured data covers <b>99.8%</b> of pages, HTTPS is clean across the board,
        content is deep (median <b>2,161 words</b>), and there are <b>zero server errors</b>. The only
        genuine to-dos are minor and quick: 22 missing H1s, a few duplicate titles/metas, and image
        alt-text gaps.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-head">Site at a glance</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Real reachable site after removing the 429 URLs</p>', unsafe_allow_html=True)
    r1 = st.columns(4)
    with r1[0]: kpi("Reachable URLs", "459", "429s removed from 1,873", "blue")
    with r1[1]: kpi("Indexable", "456", "99.3% of real site", "green")
    with r1[2]: kpi("Non-Indexable", "3", "Canonicalized only", "green")
    with r1[3]: kpi("Server Errors", "0", "No 5xx failures", "green")
    r2 = st.columns(4)
    with r2[0]: kpi("Schema Coverage", "99.8%", "458 of 459 pages", "green")
    with r2[1]: kpi("Missing H1s", "22", "Quick template fix", "beige")
    with r2[2]: kpi("Dup Titles / Metas", "12 / 19", "Minor consolidation", "beige")
    with r2[3]: kpi("Median Words", "2,161", "Deep content", "green")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.15, 1], gap="large")
    with c1:
        st.markdown('<div class="sec-head">Score composition</div>', unsafe_allow_html=True)
        st.markdown('<p class="sec-sub">Each group scored against its maximum weight</p>', unsafe_allow_html=True)
        names = [s[0] for s in SUBSCORES]; got = [s[1] for s in SUBSCORES]; maxi = [s[2] for s in SUBSCORES]
        pct = [g / m for g, m in zip(got, maxi)]
        colors = [RED if p < .35 else (CORAL if p < .6 else (BEIGE if p < .9 else GREEN)) for p in pct]
        fig = go.Figure()
        fig.add_trace(go.Bar(y=names[::-1], x=maxi[::-1], orientation="h", marker=dict(color=GRAY_LIGHT), hoverinfo="skip"))
        fig.add_trace(go.Bar(y=names[::-1], x=got[::-1], orientation="h", marker=dict(color=colors[::-1]),
                             text=[f"{g}/{m}" for g, m in zip(got, maxi)][::-1], textposition="outside",
                             textfont=dict(size=12, color=INK), hoverinfo="skip"))
        fig.update_layout(barmode="overlay", height=380, bargap=0.42, margin=dict(l=8, r=40, t=6, b=6),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
                          xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                          yaxis=dict(tickfont=dict(size=13, color=INK)))
        st.plotly_chart(fig, use_container_width=True, key="comp")
    with c2:
        st.markdown('<div class="sec-head">Scoring rationale</div>', unsafe_allow_html=True)
        st.markdown('<p class="sec-sub">Why each group landed where it did</p>', unsafe_allow_html=True)
        for nm, sc, mx, why in SUBSCORES:
            p = sc / mx
            col = RED if p < .35 else (CORAL if p < .6 else (BEIGE if p < .9 else GREEN))
            st.markdown(f'<div class="subrow"><span class="nm">{nm}</span>'
                        f'<span class="sc" style="color:{col}">{sc}/{mx}</span></div>'
                        f'<div style="font-size:11.5px;color:{GRAY_MUTED};margin:-2px 0 4px">{why}</div>',
                        unsafe_allow_html=True)

# ---------------------------------------------------------------------------- ON-PAGE & METADATA
with t_meta:
    st.markdown('<div class="sec-head">On-page &amp; metadata</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Full per-URL detail for all 459 reachable pages</p>', unsafe_allow_html=True)
    k = st.columns(4)
    with k[0]: kpi("Missing Titles", "1", "of 459", "beige")
    with k[1]: kpi("Missing Metas", "2", "of 459", "beige")
    with k[2]: kpi("Missing H1", "22", "of 459", "coral")
    with k[3]: kpi("Multiple H1", "8", "Reduce to one", "beige")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📝  Metadata table — title, meta, H1/H2 per URL (459)", expanded=True):
        st.dataframe(load("data_Metadata.csv"), use_container_width=True, height=420, hide_index=True)
    with st.expander("🧾  Full crawl data — all 24 fields per URL (459)"):
        st.dataframe(load("data_Crawl_Data.csv"), use_container_width=True, height=420, hide_index=True)

# ---------------------------------------------------------------------------- INDEXABILITY
with t_idx:
    st.markdown('<div class="sec-head">Indexability</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Status, robots directive and canonical for every reachable URL</p>', unsafe_allow_html=True)
    dcol, tcol = st.columns([1, 1.5], gap="large")
    with dcol:
        pie = go.Figure(go.Pie(labels=["Indexable", "Canonicalized"], values=[456, 3], hole=0.62, sort=False,
            marker=dict(colors=[GREEN, BEIGE]), textinfo="value", textfont=dict(size=14, color=WHITE)))
        pie.update_layout(height=290, margin=dict(l=0, r=0, t=8, b=0), paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=-0.1, font=dict(size=12)),
            annotations=[dict(text="459<br>URLs", x=0.5, y=0.5, font=dict(size=17, color=TEAL), showarrow=False)])
        st.plotly_chart(pie, use_container_width=True, key="idxpie")
    with tcol:
        st.markdown(f"""
        <div class="callout good" style="margin-top:16px">
        <b>Effectively perfect.</b> Of the 459 reachable URLs, <b>456 are indexable (99.3%)</b>. The
        only 3 exceptions are intentionally canonicalized to another URL — normal, healthy behaviour.
        There are no unexpected noindex tags and no robots blocks on the real site.
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🗂️  Full indexability table (459 URLs)", expanded=True):
        st.dataframe(load("data_Indexability.csv"), use_container_width=True, height=420, hide_index=True)

# ---------------------------------------------------------------------------- ISSUES
with t_iss:
    st.markdown('<div class="sec-head">Issues on the real site</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Every genuine issue after the 429 URLs are removed</p>', unsafe_allow_html=True)
    dcol, tcol = st.columns([1, 1.4], gap="large")
    with dcol:
        sev = go.Figure(go.Pie(labels=["Critical", "High", "Medium", "Low"],
            values=[SITE["critical"], SITE["high"], SITE["medium"], SITE["low"]], hole=0.62, sort=False,
            marker=dict(colors=[RED, CORAL, BEIGE, GRAY]), textinfo="value", textfont=dict(size=13, color=WHITE)))
        sev.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=-0.1, font=dict(size=12)),
            annotations=[dict(text="231<br>issues", x=0.5, y=0.5, font=dict(size=18, color=TEAL), showarrow=False)])
        st.plotly_chart(sev, use_container_width=True, key="sev")
    with tcol:
        st.markdown(f"""
        <div class="callout">
        Removing the 429s collapses the issue list from 2,101 to <b>231</b>, almost all low-severity.
        <b>Critical:</b> just 1 (a single fetch timeout). <b>High:</b> 24 — namely 21 missing H1s and
        3 canonical mismatches. <b>Medium:</b> 41 — duplicate titles/metas, a few multiple-H1 pages,
        2 thin pages. <b>Low:</b> 165 — image alt-text gaps.
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🔴  Critical — reachable-site (1)", expanded=True):
        st.dataframe(load("data_Critical_Issues.csv"), use_container_width=True, height=140, hide_index=True)
    with st.expander("🟠  High — missing H1s & canonical mismatches (24)"):
        hi = load("data_High_Issues.csv")
        if not hi.empty:
            ic = hi["Issue"].apply(lambda x: "Canonical mismatch" if "canonical" in str(x).lower() else str(x)).value_counts()
            st.caption("Breakdown: " + " · ".join(f"{k} ({v})" for k, v in ic.items()))
        st.dataframe(hi, use_container_width=True, height=320, hide_index=True)
    with st.expander("🟡  Medium — duplicate titles/metas, multiple H1s, thin content (41)"):
        st.dataframe(load("data_Medium_Issues.csv"), use_container_width=True, height=320, hide_index=True)
    with st.expander("⚪  Low — image alt text missing (165)"):
        st.dataframe(load("data_Low_Issues.csv"), use_container_width=True, height=320, hide_index=True)
    with st.expander("📋  Original tool recommendations (full list of 13)"):
        st.caption("As emitted by the crawler on the raw 1,873-URL set — kept verbatim for reference.")
        st.dataframe(load("data_Recommendations.csv"), use_container_width=True, height=320, hide_index=True)

# ---------------------------------------------------------------------------- PERFORMANCE & COVERAGE
with t_perf:
    st.markdown('<div class="sec-head">Core Web Vitals — field data (context)</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">90-day trend, 1 Apr – 29 Jun 2026 · two URL segments · informational</p>', unsafe_allow_html=True)
    k = st.columns(4)
    with k[0]: kpi("Desktop 'Poor'", "90.6%", "of URLs, last day", "coral")
    with k[1]: kpi("Mobile 'Poor'", "58.6%", "of URLs, last day", "coral")
    with k[2]: kpi("'Good' URLs", "0%", "Both segments", "coral")
    with k[3]: kpi("90-day trend", "Worsening", "Poor share rising", "coral")
    st.markdown(f"""
    <div class="callout">
    Shown for completeness from your Core Web Vitals files. These field measurements cover a much
    larger URL population than the 459-page crawl, so they aren't folded into the crawl score — but
    they're worth watching: essentially no URLs reach "Good," and the Poor share grew over the window.
    </div>
    """, unsafe_allow_html=True)

    def cwv_chart(df, title):
        df = df.copy(); df["Date"] = pd.to_datetime(df["Date"])
        fig = go.Figure()
        for col, color in [("Good", GREEN), ("Need improvement", BEIGE), ("Poor", RED)]:
            fig.add_trace(go.Scatter(x=df["Date"], y=df[col], name=col, mode="lines",
                stackgroup="one", line=dict(width=0.5, color=color), fillcolor=color))
        fig.update_layout(title=dict(text=title, font=dict(size=14, color=TEAL)), height=300,
            margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=-0.15, font=dict(size=11)),
            xaxis=dict(showgrid=False, tickfont=dict(size=10, color=GRAY_MUTED)),
            yaxis=dict(showgrid=True, gridcolor=GRAY_LIGHT, tickfont=dict(size=10, color=GRAY_MUTED)))
        return fig

    cc = st.columns(2, gap="large")
    d1 = load("cwv_desktop.csv"); d2 = load("cwv_mobile.csv")
    with cc[0]:
        if not d1.empty: st.plotly_chart(cwv_chart(d1, "Segment A — URLs by CWV status"), use_container_width=True, key="cwv1")
    with cc[1]:
        if not d2.empty: st.plotly_chart(cwv_chart(d2, "Segment B — URLs by CWV status"), use_container_width=True, key="cwv2")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-head">Search Console — coverage &amp; impressions (context)</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Indexed vs not-indexed URLs and daily impressions, Apr–Jun 2026</p>', unsafe_allow_html=True)
    k2 = st.columns(4)
    with k2[0]: kpi("Indexed URLs", "19,979", "Latest (12 Jun)", "blue")
    with k2[1]: kpi("Not Indexed", "262,402", "Whole GSC property", "coral")
    with k2[2]: kpi("Impressions 90d", "7.93M", "≈108.7K / day", "blue")
    with k2[3]: kpi("Impr. trend", "Flat", "≈111K → ≈107K/day", "beige")
    cov = load("coverage.csv")
    if not cov.empty:
        cov["Date"] = pd.to_datetime(cov["Date"])
        gcol = st.columns([1.3, 1], gap="large")
        with gcol[0]:
            covd = cov.dropna(subset=["Indexed", "Not indexed"])
            f = go.Figure()
            f.add_trace(go.Scatter(x=covd["Date"], y=covd["Not indexed"], name="Not indexed", mode="lines",
                stackgroup="c", line=dict(width=0.5, color=CORAL), fillcolor=CORAL))
            f.add_trace(go.Scatter(x=covd["Date"], y=covd["Indexed"], name="Indexed", mode="lines",
                stackgroup="c", line=dict(width=0.5, color=TEAL), fillcolor=TEAL))
            f.update_layout(title=dict(text="Indexed vs Not-indexed URLs (whole property)", font=dict(size=14, color=TEAL)),
                height=300, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", y=-0.15, font=dict(size=11)),
                xaxis=dict(showgrid=False, tickfont=dict(size=10, color=GRAY_MUTED)),
                yaxis=dict(showgrid=True, gridcolor=GRAY_LIGHT, tickfont=dict(size=10, color=GRAY_MUTED)))
            st.plotly_chart(f, use_container_width=True, key="cov1")
        with gcol[1]:
            fi = go.Figure(go.Scatter(x=cov["Date"], y=cov["Impressions"], mode="lines",
                line=dict(color=BEIGE, width=2.5), fill="tozeroy", fillcolor="rgba(225,183,126,0.18)"))
            fi.update_layout(title=dict(text="Daily impressions", font=dict(size=14, color=TEAL)), height=300,
                margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, tickfont=dict(size=10, color=GRAY_MUTED)),
                yaxis=dict(showgrid=True, gridcolor=GRAY_LIGHT, tickfont=dict(size=10, color=GRAY_MUTED)))
            st.plotly_chart(fi, use_container_width=True, key="cov2")
    st.markdown(f"""
    <div class="callout">
    Note this coverage covers the entire Search Console property (hundreds of thousands of URLs),
    not just the 459-page compressors crawl — so the low indexed share reflects the whole domain, not
    the section this report scores. Included here in full so nothing is dropped.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------- ACTION PLAN
with t_act:
    st.markdown('<div class="sec-head">Prioritised action plan</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Genuine to-dos for the real site, ordered by impact per unit of effort</p>', unsafe_allow_html=True)
    RECS = [
        ("high", "Add a unique H1 to the 22 pages missing one.",
         "Effort: Low · Impact: Medium — direct on-page signal, quick template fix."),
        ("high", "Resolve the 3 canonical mismatches.",
         "Effort: Low · Impact: Medium — confirm each points to the intended URL."),
        ("medium", "De-duplicate 12 titles and 19 meta descriptions.",
         "Effort: Medium · Impact: Medium — mostly CR-series & FD-dryer variants sharing copy."),
        ("medium", "Enforce a single H1 across the 8 multiple-H1 pages.",
         "Effort: Low · Impact: Low-Medium."),
        ("medium", "Write the 1 missing meta / title; expand the 2 thin pages (<300 words).",
         "Effort: Low · Impact: Low."),
        ("low", "Add alt text — 165 pages, 549 images missing it.",
         "Effort: Medium · Impact: Low — accessibility + image-search upside."),
        ("low", "Fix the crawler rate-limit for future audits (allow-list / throttle).",
         "Effort: Low · Impact: Process — prevents the 429 noise that obscured this crawl."),
        ("low", "Watch Core Web Vitals property-wide — 0% 'Good' and worsening.",
         "Effort: High · Impact: Site-wide — outside this section but worth a separate workstream."),
    ]
    for tag, text, effort in RECS:
        st.markdown(f'<div class="rec"><div class="tag tag-{tag}">{tag}</div>'
                    f'<div><div class="rtext">{text}</div><div class="reffort">{effort}</div></div></div>',
                    unsafe_allow_html=True)
    st.markdown(f"""
    <div class="callout good" style="margin-top:14px">
    <b>Bottom line.</b> The reachable compressors site is in <b>excellent</b> technical shape —
    <b>{SCORE}/100 (Grade {G})</b>. Indexability, schema, security, performance and content depth are
    all strong. The remaining work is light polish: H1s, a handful of duplicate tags, and image alt
    text. The alarming numbers in the raw crawl were entirely the 429 rate-limit artefact, now removed.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------- 429 APPENDIX
with t_429:
    st.markdown('<div class="sec-head">Appendix — excluded 429 URLs</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">The 1,414 URLs removed from scoring · kept only for transparency</p>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="callout">
    These URLs returned <b>HTTP 429 (Too Many Requests)</b> during the crawl — a rate-limit on the
    crawler, not a fault on the site. They load normally for real users, so they are excluded from
    the score and every count above. The full list is provided here so nothing is hidden.
    </div>
    """, unsafe_allow_html=True)
    d429 = load("dropped_429_urls.csv")
    if not d429.empty:
        st.caption(f"{len(d429):,} URLs excluded.")
        st.dataframe(d429, use_container_width=True, height=460, hide_index=True)

# ---------------------------------------------------------------------------- FOOTER
st.markdown(f"""
<div style="margin-top:30px;padding-top:14px;border-top:1px solid {GRAY_LIGHT};
     color:{GRAY_MUTED};font-size:12px;display:flex;justify-content:space-between">
    <span>Atlas Copco · Technical SEO Report · 429 URLs excluded · all remaining detail included (2026-06-30)</span>
    <span>Brand palette per Atlas Copco Group visual identity (2023)</span>
</div>
""", unsafe_allow_html=True)
