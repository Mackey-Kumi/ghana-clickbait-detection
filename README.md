# Detecting Clickbait and Sensationalism in Ghanaian Online News Headlines

DCIT 316 — Computational Models for Social Media Mining, University of Ghana, 2025/2026.

## Setup

```bash
pip install -r requirements.txt
```

## Stage 1 — Scraping

```bash
python -m scraper.scrape --dry-run   # fetch ~10 headlines/outlet, sanity-check selectors
python -m scraper.scrape             # full collection run, ~1,000 headlines
```

(Run as a module — `python scraper/scrape.py` directly fails with
`ModuleNotFoundError: No module named 'scraper'`, since the script's own
directory, not the project root, ends up on `sys.path`.)

Output: `data/raw/<outlet>.csv` per outlet, plus `data/raw/headlines_combined.csv`.

## Project layout

- `scraper/` — headline collection (Stage 1)
- `data/raw/` — scraped, unlabeled headlines + data card
- `data/processed/` — annotated data (Stage 2)
- `notebooks/` — modeling and EDA (Stage 3+)
- `app/` — Streamlit demo (Stage 5)
