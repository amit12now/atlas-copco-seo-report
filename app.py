"""
Atlas Copco | Technical SEO Report
==================================
Branded four-tab Streamlit dashboard built from the full 2026-06-30 dataset:
  - Crawl audit  (www.atlascopco.com/en-us/compressors, 1,873 URLs)
  - Core Web Vitals field data  x2 segments  (90 days)
  - Search Console Coverage + Impressions  (indexed vs not-indexed, 90 days)

Per client direction: HTTP 429 responses are treated as crawler rate-limit
artefacts and excluded from fault-scoring. A single reasoned score is shown.

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
TEAL       = "#054E5A"
TEAL_DARK  = "#033840"
TEAL_TINT  = "#0A6675"
GRAY       = "#A1A9B4"
GRAY_LIGHT = "#EDEFF2"
GRAY_MUTED = "#5D7875"
BEIGE      = "#E1B77E"
BLUE       = "#123F6D"
CORAL      = "#F68363"
RED        = "#C03627"
GREEN      = "#1E7D5A"
WHITE      = "#FFFFFF"
INK        = "#1A2226"

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
    .masthead .eyebrow {{ letter-spacing:3px; text-transform:uppercase; font-size:12px;
        font-weight:600; color:{BEIGE}; margin-bottom:6px; }}
    .masthead h1 {{ font-size:32px; font-weight:800; margin:0; line-height:1.15; }}
    .masthead p {{ color:{GRAY}; margin:8px 0 0; font-size:15px; }}
    .masthead .bars {{ display:inline-block; width:46px; height:5px; background:{BEIGE};
        border-radius:3px; margin-bottom:14px; }}

    .grade-pill {{ display:inline-block; padding:6px 18px; border-radius:999px;
        font-weight:700; font-size:15px; letter-spacing:0.5px; }}

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

    .sec-head {{ font-size:19px; font-weight:700; color:{TEAL}; margin:6px 0 2px;
        padding-bottom:6px; border-bottom:2px solid {GRAY_LIGHT}; }}
    .sec-sub {{ font-size:13px; color:{GRAY_MUTED}; margin:0 0 12px; }}

    .callout {{ background:{GRAY_LIGHT}; border-radius:12px; padding:16px 20px;
        border-left:5px solid {BEIGE}; margin:10px 0; font-size:14px; color:{INK}; }}
    .callout.alert {{ border-left-color:{RED}; background:#FBEDEB; }}
    .callout.good {{ border-left-color:{GREEN}; background:#E9F5EF; }}
    .callout b {{ color:{TEAL}; }}

    .stTabs [data-baseweb="tab-list"] {{ gap:6px; border-bottom:2px solid {GRAY_LIGHT}; }}
    .stTabs [data-baseweb="tab"] {{ height:46px; padding:0 20px; border-radius:10px 10px 0 0;
        font-weight:600; font-size:14.5px; color:{GRAY_MUTED}; background:transparent; }}
    .stTabs [aria-selected="true"] {{ background:{TEAL}; color:{WHITE}!important; }}

    .rec {{ display:flex; gap:14px; align-items:flex-start; padding:13px 16px;
        border:1px solid {GRAY_LIGHT}; border-radius:10px; margin-bottom:9px; background:{WHITE}; }}
    .rec .tag {{ flex-shrink:0; font-size:11px; font-weight:700; padding:3px 10px;
        border-radius:6px; text-transform:uppercase; letter-spacing:0.5px; }}
    .tag-critical {{ background:#FBEDEB; color:{RED}; }}
    .tag-high {{ background:#FDEEE7; color:{CORAL}; }}
    .tag-medium {{ background:#FBF3E6; color:#9A6B1F; }}
    .tag-low {{ background:{GRAY_LIGHT}; color:{GRAY_MUTED}; }}
    .rec .rtext {{ font-size:14px; color:{INK}; }}
    .rec .reffort {{ font-size:12px; color:{GRAY_MUTED}; margin-top:2px; }}
    .stDataFrame {{ border:1px solid {GRAY_LIGHT}; border-radius:10px; }}

    .subrow {{ display:flex; justify-content:space-between; align-items:center;
        padding:9px 4px; border-bottom:1px solid {GRAY_LIGHT}; font-size:13.5px; }}
    .subrow .nm {{ font-weight:600; color:{INK}; }}
    .subrow .sc {{ font-weight:700; }}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load(name):
    p = os.path.join(DATA_DIR, name)
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()


# ----------------------------------------------------------------------------
# FULL DATASET — every figure from all four uploaded files
# ----------------------------------------------------------------------------
AUDIT = dict(
    total_urls=1873, indexable=455, non_indexable=1418,
    err_429=1414, err_5xx=0, timeouts=1,
    missing_titles=0, missing_meta=1, missing_h1=21,
    dup_titles=12, dup_metas=19, multiple_h1=8, thin_content=1,
    broken_internal=26860, broken_source_pages=456, broken_targets=396,
    schema_cov=24.5, images_missing_alt=165,
    critical=1415, high=480, medium=41, low=165,
)

# Core Web Vitals — real field data (last-day snapshot + trend), two CWV files
CWV = dict(desktop_poor=90.6, desktop_ni=9.4, desktop_good=0.0,
           mobile_poor=58.6, mobile_ni=41.3, mobile_good=0.0, trend="worsening")

# Search Console Coverage — from the Coverage file
COV = dict(indexed=19979, not_indexed=262402, indexed_pct=7.1,
           impr_total=7933380, impr_avg=108676, impr_first14=111320,
           impr_last14=107475, idx_change=-16476, notidx_change=-485360)

# ----------------------------------------------------------------------------
# SINGLE REASONED SCORE
# 429s excluded (crawl artefact). Performance re-scored from real CWV field data.
# Indexability confirmed real by GSC coverage -> the >20% non-indexable cap applies.
# ----------------------------------------------------------------------------
SUBSCORES = [
    ("Crawlability",     18.5, 20, "429s excluded as rate-limit artefacts — only 1 genuine timeout, zero 5xx"),
    ("Indexability",      3.5, 20, "1,418/1,873 non-indexable; Search Console confirms just 7.1% indexed"),
    ("On-Page",          19.9, 20, "0 missing titles, 1 missing meta, strong heading depth"),
    ("Internal Linking",  9.5, 10, "All flagged broken links were 429s; structure otherwise sound"),
    ("Schema",            1.2,  5, "Structured-data coverage only 24.5%"),
    ("Images",            4.6,  5, "165 pages missing image alt text"),
    ("Performance",       2.0, 10, "CWV field data: 90.6% Poor desktop, 58.6% Poor / 0% Good mobile, worsening"),
    ("Security",          5.0,  5, "HTTPS clean, no mixed content, zero HTTPS errors"),
    ("Content Quality",   4.8,  5, "Only 1 thin-content page across 1,873"),
]
RAW = round(sum(s[1] for s in SUBSCORES))          # 69
SCORE = min(RAW, 65)                                # >20% non-indexable cap applies -> 65


def grade(s):
    if s >= 85: return "A", GREEN
    if s >= 75: return "B", TEAL_TINT
    if s >= 65: return "C", BEIGE
    if s >= 50: return "D", CORAL
    return "E", RED


G, GC = grade(SCORE)


def ring(score, color, size=230):
    fig = go.Figure(go.Pie(values=[score, 100 - score], hole=0.74, sort=False,
        direction="clockwise", marker=dict(colors=[color, GRAY_LIGHT]),
        textinfo="none", hoverinfo="skip"))
    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0),
        height=size, width=size, paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text=f"<b>{score}</b>", x=0.5, y=0.52, font=dict(size=58, color=color), showarrow=False),
                     dict(text="/ 100", x=0.5, y=0.30, font=dict(size=15, color=GRAY_MUTED), showarrow=False)])
    return fig


def kpi(label, value, sub="", tone=""):
    st.markdown(f'<div class="kpi {tone}"><div class="label">{label}</div>'
                f'<div class="value">{value}</div><div class="sub">{sub}</div></div>',
                unsafe_allow_html=True)


# ============================================================================ MASTHEAD
st.markdown(f"""
<div class="masthead">
    <div class="bars"></div>
    <div class="eyebrow">Technical SEO Audit · Compressors</div>
    <h1>Atlas Copco — Technical SEO Report</h1>
    <p>www.atlascopco.com/en-us/compressors&nbsp;·&nbsp;Crawl 30 Jun 2026&nbsp;·&nbsp;1,873 URLs&nbsp;·&nbsp;
       90-day Core Web Vitals &amp; Search Console coverage included</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["  Overview  ", "  Diagnostics  ",
                                  "  Performance & Coverage  ", "  Action Plan  "])

# ---------------------------------------------------------------------------- OVERVIEW
with tab1:
    left, right = st.columns([1, 1.4], gap="large")
    with left:
        st.markdown('<div class="sec-head">Technical Health Score</div>', unsafe_allow_html=True)
        st.markdown('<p class="sec-sub">One composite score across nine weighted signal groups</p>', unsafe_allow_html=True)
        st.plotly_chart(ring(SCORE, GC), use_container_width=True, key="ring")
        st.markdown(f'<div style="text-align:center;margin-top:-8px">'
                    f'<span class="grade-pill" style="background:{GC};color:{WHITE}">GRADE {G}</span></div>',
                    unsafe_allow_html=True)
    with right:
        st.markdown('<div class="sec-head">How the score was reached</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="callout">
        Per direction, all <b>HTTP 429 (Too Many Requests)</b> responses are treated as crawler
        rate-limit artefacts and excluded from fault-scoring — so crawlability and internal linking
        score near-full despite the 1,414 flagged errors and 26,860 flagged links.
        </div>
        <div class="callout alert">
        Two <b>genuine</b> problems pull the score down. <b>(1) Indexability:</b> the crawl finds
        75.7% of URLs non-indexable, and Google Search Console independently confirms only
        <b>7.1% of URLs are indexed</b>. <b>(2) Performance:</b> Core Web Vitals field data shows
        <b>90.6% of desktop URLs and 58.6% of mobile URLs rated "Poor," with 0% "Good"</b> — and the
        trend worsened over the 90-day window. Because the non-indexable share exceeds 20% and is
        corroborated, the score is capped at <b>65</b>.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-head">Site at a glance</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Headline figures across all four data sources</p>', unsafe_allow_html=True)
    r1 = st.columns(4)
    with r1[0]: kpi("URLs Crawled", "1,873", "Full compressors section", "blue")
    with r1[1]: kpi("Indexable (crawl)", "455", "24.3% of URLs", "coral")
    with r1[2]: kpi("Indexed (GSC)", "7.1%", "19,979 of 282,381", "red")
    with r1[3]: kpi("CWV 'Good'", "0%", "Desktop & mobile alike", "red")
    r2 = st.columns(4)
    with r2[0]: kpi("Missing H1s", "21", "On-page fix", "beige")
    with r2[1]: kpi("Dup Titles / Metas", "12 / 19", "Consolidation needed", "beige")
    with r2[2]: kpi("Schema Coverage", "24.5%", "Structured-data gap", "coral")
    with r2[3]: kpi("5xx Errors", "0", "No server failures", "green")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.15, 1], gap="large")
    with c1:
        st.markdown('<div class="sec-head">Score composition</div>', unsafe_allow_html=True)
        st.markdown('<p class="sec-sub">Each group scored against its maximum weight</p>', unsafe_allow_html=True)
        names = [s[0] for s in SUBSCORES]; got = [s[1] for s in SUBSCORES]; maxi = [s[2] for s in SUBSCORES]
        pct = [g / m for g, m in zip(got, maxi)]
        colors = [RED if p < .35 else (CORAL if p < .6 else (BEIGE if p < .85 else TEAL)) for p in pct]
        fig = go.Figure()
        fig.add_trace(go.Bar(y=names[::-1], x=maxi[::-1], orientation="h",
                             marker=dict(color=GRAY_LIGHT), hoverinfo="skip"))
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
            col = RED if p < .35 else (CORAL if p < .6 else (BEIGE if p < .85 else GREEN))
            st.markdown(f'<div class="subrow"><span class="nm">{nm}</span>'
                        f'<span class="sc" style="color:{col}">{sc}/{mx}</span></div>'
                        f'<div style="font-size:11.5px;color:{GRAY_MUTED};margin:-2px 0 4px">{why}</div>',
                        unsafe_allow_html=True)

# ---------------------------------------------------------------------------- DIAGNOSTICS
with tab2:
    st.markdown('<div class="sec-head">Diagnostics deep-dive</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Every affected URL from the crawl audit — expand any category</p>', unsafe_allow_html=True)

    dcol, tcol = st.columns([1, 1.4], gap="large")
    with dcol:
        sev = go.Figure(go.Pie(labels=["Critical", "High", "Medium", "Low"],
            values=[AUDIT["critical"], AUDIT["high"], AUDIT["medium"], AUDIT["low"]], hole=0.62, sort=False,
            marker=dict(colors=[RED, CORAL, BEIGE, GRAY]), textinfo="value", textfont=dict(size=13, color=WHITE)))
        sev.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=-0.1, font=dict(size=12)),
            annotations=[dict(text="2,101<br>issues", x=0.5, y=0.5, font=dict(size=18, color=TEAL), showarrow=False)])
        st.plotly_chart(sev, use_container_width=True, key="sev")
    with tcol:
        st.markdown(f"""
        <div class="callout" style="margin-top:20px">
        <b>Reading the severity split.</b> Of the 1,415 "critical" rows, 1,414 are 429 rate-limits
        (excluded from scoring) and 1 is a genuine fetch timeout. The <b>High</b> band holds the real,
        addressable on-page work: <b>21 missing H1s</b>, <b>3 canonical issues</b>, plus broken-link
        references across 456 pages (429-driven). <b>Medium:</b> 12 duplicate titles, 19 duplicate
        metas, 8 multiple-H1 pages, 1 thin page. <b>Low:</b> 165 pages missing image alt text.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🔴  Critical — 4xx / unreachable URLs  (1,415)"):
        st.caption("1,414 rows are HTTP 429 (rate-limit, excluded from scoring); 1 is a genuine timeout.")
        st.dataframe(load("data_Critical_Issues.csv"), use_container_width=True, height=320, hide_index=True)
    with st.expander("🟠  High — missing H1s, canonicals & broken-link pages  (480)"):
        hi = load("data_High_Issues.csv")
        if not hi.empty:
            ic = hi["Issue"].apply(lambda x: "Broken internal links" if "broken" in str(x).lower() else str(x)).value_counts()
            st.caption("Breakdown: " + " · ".join(f"{k} ({v})" for k, v in ic.items()))
        st.dataframe(hi, use_container_width=True, height=320, hide_index=True)
    with st.expander("🟡  Medium — duplicate titles/metas, multiple H1s, thin content  (41)"):
        st.dataframe(load("data_Medium_Issues.csv"), use_container_width=True, height=300, hide_index=True)
    with st.expander("⚪  Low — missing image alt text  (165)"):
        st.dataframe(load("data_Low_Issues.csv"), use_container_width=True, height=300, hide_index=True)
    with st.expander("🔗  Broken internal links — most-referenced 429 targets (396 unique)"):
        st.caption("All returned 429 — fixing the edge rate-limit clears every row at once.")
        st.dataframe(load("data_broken_targets.csv").head(80), use_container_width=True, height=320, hide_index=True)
    with st.expander("🗂️  Indexability detail — full crawl status (1,873 URLs)"):
        st.dataframe(load("data_Indexability.csv"), use_container_width=True, height=340, hide_index=True)
    with st.expander("📝  Metadata — titles, metas, H1/H2 per URL (1,873)"):
        st.dataframe(load("data_Metadata.csv"), use_container_width=True, height=340, hide_index=True)

# ---------------------------------------------------------------------------- PERFORMANCE & COVERAGE
with tab3:
    st.markdown('<div class="sec-head">Core Web Vitals — field data</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">90-day trend, 1 Apr – 29 Jun 2026 · two URL segments</p>', unsafe_allow_html=True)

    k = st.columns(4)
    with k[0]: kpi("Desktop 'Poor'", "90.6%", "of URLs, last day", "red")
    with k[1]: kpi("Mobile 'Poor'", "58.6%", "of URLs, last day", "coral")
    with k[2]: kpi("'Good' URLs", "0%", "Both segments", "red")
    with k[3]: kpi("90-day trend", "Worsening", "Poor share rising", "red")

    st.markdown(f"""
    <div class="callout alert">
    The audit tool scored performance a blind <b>10/10</b>, but the actual Core Web Vitals field
    data tells the opposite story. Across the full 90-day window essentially <b>no URLs reach
    "Good,"</b> the majority sit in <b>"Poor,"</b> and the Poor share <i>grew</i> over time. This is
    the single largest correction in the report and the reason Performance is re-scored to 2/10.
    </div>
    """, unsafe_allow_html=True)

    def cwv_chart(df, title):
        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        fig = go.Figure()
        for col, color in [("Good", GREEN), ("Need improvement", BEIGE), ("Poor", RED)]:
            fig.add_trace(go.Scatter(x=df["Date"], y=df[col], name=col, mode="lines",
                stackgroup="one", line=dict(width=0.5, color=color), fillcolor=color))
        fig.update_layout(title=dict(text=title, font=dict(size=14, color=TEAL)),
            height=300, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h", y=-0.15, font=dict(size=11)),
            xaxis=dict(showgrid=False, tickfont=dict(size=10, color=GRAY_MUTED)),
            yaxis=dict(showgrid=True, gridcolor=GRAY_LIGHT, tickfont=dict(size=10, color=GRAY_MUTED)))
        return fig

    cc = st.columns(2, gap="large")
    d1 = load("cwv_desktop.csv"); d2 = load("cwv_mobile.csv")
    with cc[0]:
        if not d1.empty:
            st.plotly_chart(cwv_chart(d1, "Segment A — URLs by CWV status"), use_container_width=True, key="cwv1")
    with cc[1]:
        if not d2.empty:
            st.plotly_chart(cwv_chart(d2, "Segment B — URLs by CWV status"), use_container_width=True, key="cwv2")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-head">Search Console — coverage &amp; impressions</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Indexed vs not-indexed URLs and daily impressions, Apr–Jun 2026</p>', unsafe_allow_html=True)

    k2 = st.columns(4)
    with k2[0]: kpi("Indexed URLs", "19,979", "Latest (12 Jun)", "coral")
    with k2[1]: kpi("Not Indexed", "262,402", "92.9% of known URLs", "red")
    with k2[2]: kpi("Indexed Share", "7.1%", "Corroborates crawl", "red")
    with k2[3]: kpi("Impressions (90d)", "7.93M", "≈108.7K / day", "blue")

    cov = load("coverage.csv")
    if not cov.empty:
        cov["Date"] = pd.to_datetime(cov["Date"])
        gcol = st.columns([1.3, 1], gap="large")
        with gcol[0]:
            covd = cov.dropna(subset=["Indexed", "Not indexed"])
            f = go.Figure()
            f.add_trace(go.Scatter(x=covd["Date"], y=covd["Not indexed"], name="Not indexed",
                mode="lines", stackgroup="c", line=dict(width=0.5, color=RED), fillcolor=RED))
            f.add_trace(go.Scatter(x=covd["Date"], y=covd["Indexed"], name="Indexed",
                mode="lines", stackgroup="c", line=dict(width=0.5, color=TEAL), fillcolor=TEAL))
            f.update_layout(title=dict(text="Indexed vs Not-indexed URLs", font=dict(size=14, color=TEAL)),
                height=300, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h", y=-0.15, font=dict(size=11)),
                xaxis=dict(showgrid=False, tickfont=dict(size=10, color=GRAY_MUTED)),
                yaxis=dict(showgrid=True, gridcolor=GRAY_LIGHT, tickfont=dict(size=10, color=GRAY_MUTED)))
            st.plotly_chart(f, use_container_width=True, key="cov1")
        with gcol[1]:
            fi = go.Figure(go.Scatter(x=cov["Date"], y=cov["Impressions"], mode="lines",
                line=dict(color=BEIGE, width=2.5), fill="tozeroy", fillcolor="rgba(225,183,126,0.18)"))
            fi.update_layout(title=dict(text="Daily impressions", font=dict(size=14, color=TEAL)),
                height=300, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, tickfont=dict(size=10, color=GRAY_MUTED)),
                yaxis=dict(showgrid=True, gridcolor=GRAY_LIGHT, tickfont=dict(size=10, color=GRAY_MUTED)))
            st.plotly_chart(fi, use_container_width=True, key="cov2")

    st.markdown(f"""
    <div class="callout">
    Not-indexed URLs did fall sharply over the window (from ~748K to ~262K), which is progress — but
    the <b>indexed count also declined</b> (36,455 → 19,979), so the improvement is mostly Google
    dropping URLs from its known set rather than promoting them into the index. Impressions held
    roughly flat (≈111K/day → ≈107K/day), meaning visibility isn't yet benefiting.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------- ACTION PLAN
with tab4:
    st.markdown('<div class="sec-head">Prioritised action plan</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Sequenced across all four data sources for maximum recovery per unit of effort</p>', unsafe_allow_html=True)
    RECS = [
        ("critical", "Fix Core Web Vitals — 0% of URLs are 'Good' and the trend is worsening.",
         "Effort: High · Impact: Very High — target LCP, CLS & INP; biggest single score lever (Performance 2/10)."),
        ("critical", "Resolve the indexability gap — GSC confirms only 7.1% of URLs indexed.",
         "Effort: High · Impact: Very High — audit noindex/canonical rules on the 1,418 non-indexable URLs; lifts the 65 cap."),
        ("high", "Re-crawl behind a throttle / allow-list the crawler IP.",
         "Effort: Low · Impact: High — clears all 1,414 '429' flags and 26,860 broken-link flags at once."),
        ("high", "Add a unique H1 to the 21 pages missing one.",
         "Effort: Low · Impact: Medium — direct on-page signal, quick template fix."),
        ("high", "Resolve canonical issues on the 3 affected pages.",
         "Effort: Low · Impact: Medium — prevents index dilution."),
        ("medium", "De-duplicate 12 titles and 19 meta descriptions.",
         "Effort: Medium · Impact: Medium — mostly CR-series & FD-dryer variants sharing copy."),
        ("medium", "Enforce a single H1 across the 8 multiple-H1 pages.",
         "Effort: Low · Impact: Low-Medium."),
        ("medium", "Write the 1 missing meta description; expand the 1 thin-content page (<300 words).",
         "Effort: Low · Impact: Low."),
        ("low", "Add alt text to images across 165 pages.",
         "Effort: Medium · Impact: Low — accessibility + image-search upside."),
        ("low", "Roll out structured data — coverage is only 24.5%.",
         "Effort: High · Impact: Medium — Product / Breadcrumb / FAQ schema for rich results."),
    ]
    for tag, text, effort in RECS:
        st.markdown(f'<div class="rec"><div class="tag tag-{tag}">{tag}</div>'
                    f'<div><div class="rtext">{text}</div><div class="reffort">{effort}</div></div></div>',
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-head">Projected recovery</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Illustrative trajectory as fixes land — indicative, not guaranteed</p>', unsafe_allow_html=True)
    stages = ["Today", "+ Throttled\nre-crawl", "+ Indexability\nfixes", "+ CWV\n& schema"]
    vals = [SCORE, 68, 82, 90]
    line = go.Figure(go.Scatter(x=stages, y=vals, mode="lines+markers+text",
        text=[str(v) for v in vals], textposition="top center",
        textfont=dict(size=15, color=TEAL), line=dict(color=TEAL, width=4),
        marker=dict(size=14, color=[GC, BEIGE, TEAL_TINT, GREEN], line=dict(color=WHITE, width=2)),
        fill="tozeroy", fillcolor="rgba(5,78,90,0.07)"))
    line.update_layout(height=330, margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
        yaxis=dict(range=[0, 100], showgrid=True, gridcolor=GRAY_LIGHT, tickfont=dict(color=GRAY_MUTED)),
        xaxis=dict(tickfont=dict(size=12, color=INK)))
    st.plotly_chart(line, use_container_width=True, key="recovery")

    st.markdown(f"""
    <div class="callout">
    <b>Bottom line.</b> On-page, security and content quality are strong. But two evidence-backed
    problems hold the score at <b>{SCORE}/100 (Grade {G})</b>: a real <b>indexability</b> gap
    confirmed by Search Console (7.1% indexed) and genuinely <b>poor Core Web Vitals</b> (0% of URLs
    "Good," worsening). Fix those two first and the realistic ceiling sits around the low-90s.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------- FOOTER
st.markdown(f"""
<div style="margin-top:30px;padding-top:14px;border-top:1px solid {GRAY_LIGHT};
     color:{GRAY_MUTED};font-size:12px;display:flex;justify-content:space-between">
    <span>Atlas Copco · Technical SEO Report · crawl + Core Web Vitals + Search Console coverage (2026-06-30)</span>
    <span>Brand palette per Atlas Copco Group visual identity (2023)</span>
</div>
""", unsafe_allow_html=True)
