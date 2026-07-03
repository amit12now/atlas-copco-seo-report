# Atlas Copco — Technical SEO Report (Streamlit)

Branded four-tab dashboard built from the **complete** 2026-06-30 dataset:
crawl audit + Core Web Vitals field data (2 segments) + Search Console coverage.

## Run locally
    pip install -r requirements.txt
    streamlit run app.py

## Deploy to Streamlit Community Cloud
Push app.py, requirements.txt, and the /data folder to a public GitHub repo,
then point share.streamlit.io at app.py.

## Tabs
1. Overview — single score + grade, rationale, KPIs, score composition.
2. Diagnostics — severity split + every affected URL (crawl audit).
3. Performance & Coverage — 90-day Core Web Vitals trend and Search Console
   indexed-vs-not-indexed + impressions.
4. Action Plan — prioritised fixes + projected recovery.

## Single score — how it was reached  (65 / 100, Grade C)
- HTTP 429 responses (1,414 "4xx" + 26,860 "broken links") are treated as
  crawler rate-limit artefacts and EXCLUDED from fault-scoring.
- Performance is re-scored from the real Core Web Vitals field data
  (0% of URLs "Good", 90.6% Poor desktop / 58.6% Poor mobile, worsening).
- Indexability is a genuine, corroborated problem: crawl finds 75.7%
  non-indexable and Search Console confirms only 7.1% of URLs indexed.
- Because the corroborated non-indexable share exceeds 20%, the composite
  (raw 69) is capped at 65.

Brand palette follows the Atlas Copco Group 2023 visual identity
(Teal #054E5A primary, beige #E1B77E, deep blue #123F6D accents).
