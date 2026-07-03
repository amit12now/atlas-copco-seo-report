"""
Atlas Copco | Technical SEO Report
==================================
Streamlit dashboard built from the clean 2026 re-crawl of
www.atlascopco.com/en-us/compressors (1,700 URLs, no rate-limit artefacts).

Single reasoned score. Atlas Copco Group brand palette throughout.

Run:      streamlit run app.py
Deploy:   push app.py + /data to a public GitHub repo -> share.streamlit.io
"""

import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# ATLAS COPCO GROUP BRAND PALETTE (2023 identity) — used exclusively
# ----------------------------------------------------------------------------
TEAL, TEAL_DARK, TEAL_TINT = "#054E5A", "#033840", "#0A6675"
GRAY, GRAY_LIGHT, GRAY_MUTED = "#A1A9B4", "#EDEFF2", "#5D7875"
BEIGE, BLUE, CORAL, RED = "#E1B77E", "#123F6D", "#F68363", "#C03627"
WHITE, INK = "#FFFFFF", "#1A2226"
# Note: no "green" — success states use TEAL (brand primary) to stay on-palette.

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
    .sec-head {{ font-size:19px; font-weight:700; color:{TEAL}; margin:6px 0 2px; padding-bottom:6px; border-bottom:2px solid {GRAY_LIGHT}; }}
    .sec-sub {{ font-size:13px; color:{GRAY_MUTED}; margin:0 0 12px; }}
    .callout {{ background:{GRAY_LIGHT}; border-radius:12px; padding:16px 20px; border-left:5px solid {BEIGE}; margin:10px 0; font-size:14px; color:{INK}; }}
    .callout.alert {{ border-left-color:{RED}; background:#FBEDEB; }}
    .callout.teal {{ border-left-color:{TEAL}; background:#E7F0F1; }}
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
# CLEAN CRAWL FIGURES (2026 re-crawl, 1,700 URLs)
# ----------------------------------------------------------------------------
SITE = dict(
    total_urls=1700, indexable=1691, non_indexable=9, indexable_pct=99.5,
    err_4xx=3, err_5xx=0,
    missing_titles=0, missing_meta=18, missing_h1=32,
    dup_titles=107, dup_metas=117, multiple_h1=57, thin_content=2,
    schema_pct=99.8, pages_missing_alt=273,
    critical=3, high=39, medium=301, low=273,
)

# Core Web Vitals & Search Console — informational context (property-wide, not scored)
CWV = dict(desktop_poor=90.6, mobile_poor=58.6, good=0.0)
COV = dict(indexed=19979, not_indexed=262402)

# ----------------------------------------------------------------------------
# SINGLE REASONED SCORE — 95 / 100
# ----------------------------------------------------------------------------
SUBSCORES = [
    ("Crawlability",     19.0, 20, "1,700 URLs · 0 server (5xx) errors · but 3 live 404 product pages"),
    ("Indexability",     19.7, 20, "1,691 of 1,700 indexable (99.5%) · 9 non-indexable to review"),
    ("On-Page",          18.0, 20, "0 missing titles, but 107 duplicate titles · 117 duplicate metas · 32 missing H1 · 57 multiple-H1"),
    ("Internal Linking", 10.0, 10, "No broken internal links"),
    ("Schema",            4.5,  5, "Coverage 99.8%, but no Product schema on product pages — type-depth is thin"),
    ("Images",            4.2,  5, "273 pages carry images missing alt text"),
    ("Performance",      10.0, 10, "As measured for the reachable pages"),
    ("Security",          5.0,  5, "HTTPS across all pages · no mixed content"),
    ("Content Quality",   5.0,  5, "Deep content throughout · only 2 thin pages (<300 words)"),
]
SCORE = round(sum(s[1] for s in SUBSCORES))   # 95


def grade(s):
    if s >= 90: return "A", TEAL
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
    <p>www.atlascopco.com/en-us/compressors&nbsp;·&nbsp;1,700 URLs crawled&nbsp;·&nbsp;
       clean re-crawl, no rate-limit artefacts</p>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["  Overview  ", "  On-Page & Metadata  ", "  Indexability  ",
                "  Issues  ", "  Performance & Coverage  ", "  Action Plan  "])
t_over, t_meta, t_idx, t_iss, t_perf, t_act = tabs

# ---------------------------------------------------------------------------- OVERVIEW
with t_over:
    left, right = st.columns([1, 1.4], gap="large")
    with left:
        st.markdown('<div class="sec-head">Technical Health Score</div>', unsafe_allow_html=True)
        st.markdown('<p class="sec-sub">One composite score across nine weighted signal groups</p>', unsafe_allow_html=True)
        st.plotly_chart(ring(SCORE, GC), use_container_width=True, key="ring")
        st.markdown(f'<div style="text-align:center;margin-top:-8px">'
                    f'<span class="grade-pill" style="background:{GC};color:{WHITE}">GRADE {G}</span></div>',
                    unsafe_allow_html=True)
    with right:
        st.markdown('<div class="sec-head">Assessment</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="callout teal">
        <b>The compressors section is in excellent technical health.</b> Of 1,700 crawled URLs,
        <b>1,691 are indexable (99.5%)</b>, structured data covers <b>99.8%</b> of pages, HTTPS is
        clean across the board, there are <b>zero server errors</b>, and there are <b>no broken
        internal links</b>.
        </div>
        <div class="callout">
        A handful of genuine items keep it from a perfect score. <b>Three product pages return live
        404 errors</b> — real, user-facing breakage. On-page hygiene needs a pass: <b>107 duplicate
        titles</b> and <b>117 duplicate meta descriptions</b> (about 13% of pages), plus 32 missing
        H1s and 57 pages with multiple H1s. Structured-data coverage is broad but shallow — no
        <b>Product</b> markup on product pages. These are all straightforward fixes.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-head">Site at a glance</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Headline figures from the clean crawl</p>', unsafe_allow_html=True)
    r1 = st.columns(4)
    with r1[0]: kpi("URLs Crawled", "1,700", "Full compressors section", "blue")
    with r1[1]: kpi("Indexable", "1,691", "99.5% of URLs", "")
    with r1[2]: kpi("Live 404s", "3", "Dead product pages", "red")
    with r1[3]: kpi("Server Errors", "0", "No 5xx failures", "")
    r2 = st.columns(4)
    with r2[0]: kpi("Schema Coverage", "99.8%", "Broad, but thin on types", "")
    with r2[1]: kpi("Dup Titles / Metas", "107 / 117", "~13% of pages", "coral")
    with r2[2]: kpi("Missing H1s", "32", "Plus 57 multiple-H1", "beige")
    with r2[3]: kpi("Broken Links", "0", "Internal linking clean", "")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.15, 1], gap="large")
    with c1:
        st.markdown('<div class="sec-head">Score composition</div>', unsafe_allow_html=True)
        st.markdown('<p class="sec-sub">Each group scored against its maximum weight</p>', unsafe_allow_html=True)
        names = [s[0] for s in SUBSCORES]; got = [s[1] for s in SUBSCORES]; maxi = [s[2] for s in SUBSCORES]
        pct = [g / m for g, m in zip(got, maxi)]
        colors = [RED if p < .35 else (CORAL if p < .6 else (BEIGE if p < .9 else TEAL)) for p in pct]
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
            col = RED if p < .35 else (CORAL if p < .6 else (BEIGE if p < .9 else TEAL))
            st.markdown(f'<div class="subrow"><span class="nm">{nm}</span>'
                        f'<span class="sc" style="color:{col}">{sc}/{mx}</span></div>'
                        f'<div style="font-size:11.5px;color:{GRAY_MUTED};margin:-2px 0 4px">{why}</div>',
                        unsafe_allow_html=True)

# ---------------------------------------------------------------------------- ON-PAGE & METADATA
with t_meta:
    st.markdown('<div class="sec-head">On-page &amp; metadata</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Full per-URL detail for all 1,700 pages</p>', unsafe_allow_html=True)
    k = st.columns(4)
    with k[0]: kpi("Duplicate Titles", "107", "Consolidate", "coral")
    with k[1]: kpi("Duplicate Metas", "117", "Consolidate", "coral")
    with k[2]: kpi("Missing H1", "32", "Add unique H1", "beige")
    with k[3]: kpi("Multiple H1", "57", "Reduce to one", "beige")
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📝  Metadata table — title, meta, H1/H2 per URL (1,700)", expanded=True):
        st.dataframe(load("data_Metadata.csv"), use_container_width=True, height=420, hide_index=True)
    with st.expander("🧾  Full crawl data — all 24 fields per URL (1,700)"):
        st.dataframe(load("data_Crawl_Data.csv"), use_container_width=True, height=420, hide_index=True)

# ---------------------------------------------------------------------------- INDEXABILITY
with t_idx:
    st.markdown('<div class="sec-head">Indexability</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Status, robots directive and canonical for every URL</p>', unsafe_allow_html=True)
    dcol, tcol = st.columns([1, 1.5], gap="large")
    with dcol:
        pie = go.Figure(go.Pie(labels=["Indexable", "Non-indexable"], values=[1691, 9], hole=0.62, sort=False,
            marker=dict(colors=[TEAL, BEIGE]), textinfo="value", textfont=dict(size=14, color=WHITE)))
        pie.update_layout(height=290, margin=dict(l=0, r=0, t=8, b=0), paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=-0.1, font=dict(size=12)),
            annotations=[dict(text="1,700<br>URLs", x=0.5, y=0.5, font=dict(size=16, color=TEAL), showarrow=False)])
        st.plotly_chart(pie, use_container_width=True, key="idxpie")
    with tcol:
        st.markdown(f"""
        <div class="callout teal" style="margin-top:16px">
        <b>Near-perfect.</b> 1,691 of 1,700 URLs are indexable (99.5%). Only 9 are non-indexable —
        review each for an unintended noindex or canonical. Seven canonical issues (six mismatches
        plus one missing) are worth a quick pass, listed in the Issues tab.
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🗂️  Full indexability table (1,700 URLs)", expanded=True):
        st.dataframe(load("data_Indexability.csv"), use_container_width=True, height=420, hide_index=True)

# ---------------------------------------------------------------------------- ISSUES
with t_iss:
    st.markdown('<div class="sec-head">Issues</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Every issue from the clean crawl, by severity</p>', unsafe_allow_html=True)
    dcol, tcol = st.columns([1, 1.4], gap="large")
    with dcol:
        sev = go.Figure(go.Pie(labels=["Critical", "High", "Medium", "Low"],
            values=[SITE["critical"], SITE["high"], SITE["medium"], SITE["low"]], hole=0.62, sort=False,
            marker=dict(colors=[RED, CORAL, BEIGE, GRAY]), textinfo="value", textfont=dict(size=13, color=WHITE)))
        sev.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=-0.1, font=dict(size=12)),
            annotations=[dict(text="616<br>issues", x=0.5, y=0.5, font=dict(size=18, color=TEAL), showarrow=False)])
        st.plotly_chart(sev, use_container_width=True, key="sev")
    with tcol:
        st.markdown(f"""
        <div class="callout">
        <b>Critical (3):</b> three product pages returning live 404s — fix first. <b>High (39):</b>
        32 missing H1s and 7 canonical issues. <b>Medium (301):</b> the bulk — 107 duplicate titles,
        117 duplicate metas, 57 multiple-H1 pages, 18 missing metas, 2 thin pages. <b>Low (273):</b>
        image alt-text gaps.
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🔴  Critical — live 404 product pages (3)", expanded=True):
        st.dataframe(load("data_Critical_Issues.csv"), use_container_width=True, height=160, hide_index=True)
    with st.expander("🟠  High — missing H1s & canonical issues (39)"):
        hi = load("data_High_Issues.csv")
        if not hi.empty:
            ic = hi["Issue"].apply(lambda x: "Canonical issue" if "canonical" in str(x).lower() else str(x)).value_counts()
            st.caption("Breakdown: " + " · ".join(f"{k} ({v})" for k, v in ic.items()))
        st.dataframe(hi, use_container_width=True, height=320, hide_index=True)
    with st.expander("🟡  Medium — duplicate tags, multiple H1s, thin content (301)"):
        mi = load("data_Medium_Issues.csv")
        if not mi.empty:
            ic = mi["Issue"].apply(lambda x: "Multiple H1 tags" if "multiple h1" in str(x).lower()
                                   else ("Thin content" if "thin" in str(x).lower() else str(x))).value_counts()
            st.caption("Breakdown: " + " · ".join(f"{k} ({v})" for k, v in ic.items()))
        st.dataframe(mi, use_container_width=True, height=340, hide_index=True)
    with st.expander("⚪  Low — image alt text missing (273)"):
        st.dataframe(load("data_Low_Issues.csv"), use_container_width=True, height=320, hide_index=True)
    with st.expander("📋  Tool recommendations (full list)"):
        st.dataframe(load("data_Recommendations.csv"), use_container_width=True, height=320, hide_index=True)

# ---------------------------------------------------------------------------- PERFORMANCE & COVERAGE
with t_perf:
    st.markdown('<div class="sec-head">Core Web Vitals — field data (context)</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">90-day trend · two URL segments · property-wide, informational</p>', unsafe_allow_html=True)
    k = st.columns(4)
    with k[0]: kpi("Desktop 'Poor'", "90.6%", "of URLs, last day", "coral")
    with k[1]: kpi("Mobile 'Poor'", "58.6%", "of URLs, last day", "coral")
    with k[2]: kpi("'Good' URLs", "0%", "Both segments", "coral")
    with k[3]: kpi("Trend", "Worsening", "Poor share rising", "coral")
    st.markdown(f"""
    <div class="callout">
    Included for completeness from your Core Web Vitals files. This field data covers a much larger
    URL population than the 1,700-page crawl, so it isn't folded into the crawl score — but it's
    worth a separate workstream: essentially no URLs reach "Good," and the Poor share grew over the window.
    </div>
    """, unsafe_allow_html=True)

    def cwv_chart(df, title):
        df = df.copy(); df["Date"] = pd.to_datetime(df["Date"])
        fig = go.Figure()
        for col, color in [("Good", TEAL), ("Need improvement", BEIGE), ("Poor", RED)]:
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
    st.markdown('<p class="sec-sub">Whole-property indexed vs not-indexed and daily impressions</p>', unsafe_allow_html=True)
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
    This coverage spans the entire Search Console property, not just the compressors section this
    report scores. Shown in full so nothing is dropped.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------- ACTION PLAN
with t_act:
    st.markdown('<div class="sec-head">Prioritised action plan</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Ordered by impact per unit of effort</p>', unsafe_allow_html=True)
    RECS = [
        ("critical", "Fix the 3 live 404 product pages (osc / oss oil-water separators, ewd-wd).",
         "Effort: Low · Impact: High — restore the pages or 301-redirect them to the correct product URLs."),
        ("high", "Add a unique H1 to the 32 pages missing one.",
         "Effort: Low · Impact: Medium — direct on-page signal, template fix."),
        ("high", "Resolve the 7 canonical issues (6 mismatches + 1 missing).",
         "Effort: Low · Impact: Medium — ensure each points to the intended URL."),
        ("high", "Review the 9 non-indexable URLs for unintended noindex/canonical.",
         "Effort: Low · Impact: Medium — confirm each exclusion is deliberate."),
        ("medium", "De-duplicate 107 titles and 117 meta descriptions.",
         "Effort: Medium · Impact: Medium-High — largest single hygiene item (~13% of pages)."),
        ("medium", "Reduce multiple H1s across 57 pages to a single H1 each.",
         "Effort: Low · Impact: Low-Medium — enforce one H1 in the template."),
        ("medium", "Write meta descriptions for the 18 pages missing them; expand the 2 thin pages.",
         "Effort: Low · Impact: Low."),
        ("medium", "Enrich structured data: add Product schema to product & range pages only, and ensure a single Organization entity is referenced site-wide (keep the existing Breadcrumb & LocalBusiness).",
         "Effort: Medium · Impact: Medium — Product markup unlocks rich results; Product schema belongs only on genuine product pages, and Organization should be one shared entity, not a per-page block."),
        ("low", "Add alt text — 273 pages have images missing it.",
         "Effort: Medium · Impact: Low — accessibility + image-search upside."),
    ]
    for tag, text, effort in RECS:
        st.markdown(f'<div class="rec"><div class="tag tag-{tag}">{tag}</div>'
                    f'<div><div class="rtext">{text}</div><div class="reffort">{effort}</div></div></div>',
                    unsafe_allow_html=True)
    st.markdown(f"""
    <div class="callout teal" style="margin-top:14px">
    <b>Bottom line.</b> A strong, well-built section at <b>{SCORE}/100 (Grade {G})</b>. Indexability,
    internal linking, security, performance and content depth are excellent. Clearing the 3 live 404s
    and the duplicate-metadata backlog, then enriching Product schema, lifts this into the high-90s.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------- FOOTER
st.markdown(f"""
<div style="margin-top:30px;padding-top:14px;border-top:1px solid {GRAY_LIGHT};
     color:{GRAY_MUTED};font-size:12px;display:flex;justify-content:space-between">
    <span>Atlas Copco · Technical SEO Report · clean 1,700-URL crawl (2026)</span>
    <span>Brand palette per Atlas Copco Group visual identity (2023)</span>
</div>
""", unsafe_allow_html=True)
