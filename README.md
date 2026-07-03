# Atlas Copco — Technical SEO Report (Streamlit)

Branded three-tab dashboard built from the 2026-06-30 crawl audit of
`www.atlascopco.com/en-us/compressors`.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud
1. Push `app.py`, `requirements.txt`, and the `/data` folder to a public GitHub repo.
2. Go to share.streamlit.io → New app → point it at `app.py`.

## Structure
- `app.py` — the report (Overview / Diagnostics / Action Plan tabs)
- `data/` — cleaned CSVs exported from the source audit workbook
- Brand palette follows the Atlas Copco Group 2023 visual identity (Teal #054E5A primary).

## Scoring
Two scores are shown by design:
- **Reported 63/100** — crawler output at face value (hard-capped at 65 by the >20% non-indexable rule).
- **Adjusted 78/100** — re-scores crawlability & internal-linking on the finding that all 1,414 "4xx" errors and 26,860 "broken links" are HTTP 429 (rate-limit) artefacts, not genuine defects. Every real issue stays fully penalised.
