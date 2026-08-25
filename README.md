# Detecting Clickbait and Sensationalism in Ghanaian Online News Headlines

DCIT 316 — Computational Models for Social Media Mining, University of Ghana, 2025/2026.

## Setup

```bash
pip install -r requirements.txt
```

## Stage 1 — Scraping

```bash
python scraper/scrape.py --dry-run   # fetch ~10 headlines/outlet, sanity-check selectors
python scraper/scrape.py             # full collection run, ~1,000 headlines
```

Output: `data/raw/<outlet>.csv` per outlet, plus `data/raw/headlines_combined.csv`.

## Project layout

- `scraper/` — headline collection (Stage 1)
- `data/raw/` — scraped, unlabeled headlines + data card
- `data/processed/` — annotated data (Stage 2)
- `notebooks/` — modeling and EDA (Stage 3+)
- `app/` — Streamlit demo (Stage 5)
