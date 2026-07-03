# Atlas Copco — Technical SEO Report (Streamlit)

Branded six-tab dashboard built from the clean 2026 re-crawl of
www.atlascopco.com/en-us/compressors (1,700 URLs, no rate-limit artefacts).

## Run locally
    pip install -r requirements.txt
    streamlit run app.py

## Deploy to Streamlit Community Cloud
Push app.py, requirements.txt, and the /data folder to a public GitHub repo,
then point share.streamlit.io at app.py.

## Tabs
1. Overview — single score (95/100, Grade A), assessment, KPIs, composition.
2. On-Page & Metadata — full per-URL metadata + all 24 crawl fields (1,700 URLs).
3. Indexability — status/robots/canonical for every URL.
4. Issues — every issue by severity (Critical/High/Medium/Low) + tool recommendations.
5. Performance & Coverage — Core Web Vitals + Search Console context (property-wide, not scored).
6. Action Plan — prioritised fixes, incl. Product/Organization schema guidance.

## Single score — 95 / 100 (Grade A)
Excellent site: 1,691/1,700 indexable (99.5%), schema on 99.8% of pages, HTTPS
clean, 0 server errors, 0 broken internal links. Held back by 3 live 404 product
pages, a duplicate-metadata backlog (107 titles / 117 metas), 32 missing H1s, and
thin structured-data type-depth (no Product schema on product pages).

Brand palette follows the Atlas Copco Group 2023 visual identity
(Teal #054E5A primary, beige #E1B77E, deep blue #123F6D accents). No off-brand colors.
