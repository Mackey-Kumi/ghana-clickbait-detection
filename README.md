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

## Stage 2 — Annotation

`data/processed/pre_labels.csv` (all 1,000 headlines) and
`data/processed/second_annotator_subset.csv` (the 250-headline blind subset)
are already generated. Codebook: `docs/ANNOTATION_CODEBOOK.md`.

Send your second annotator `second_annotator_subset.xlsx`, not the `.csv` —
same 250 headlines, but the `label` column has a dropdown (Clickbait /
Informative / Ambiguous) instead of requiring them to type the label by hand.

```bash
python -m annotate.verify              # your verification pass -- resumable, stop/start anytime
```

Send `data/processed/second_annotator_subset.csv` to your second annotator
(never `second_annotator_mapping.csv` — that's the private id→url key).
Once they return it filled in:

```bash
python -m annotate.kappa path/to/their-completed-subset.csv
python -m annotate.merge_final         # only after your verify.py pass is 100% complete
```

Output: `data/processed/annotated_headlines.csv` — 1,000 labeled headlines
(Clickbait/Informative/Ambiguous), ready for Stage 3 modeling.

## Stage 3 — Baseline model

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/baseline.ipynb
```

TF-IDF (unigrams+bigrams) + Logistic Regression, class-balanced. Reuses
`models.data.load_labeled_dataset()`/`make_train_test_split()` (seed 42) so
Stages 4 and 5 evaluate on the identical test set. Includes a held-out-outlet
generalization check (train on 6 outlets, test on the 7th) alongside the
standard 80/20 split, and a top-features table. Output:
`notebooks/baseline_confusion_matrix.png` plus the full results inline in the
notebook.

## Project layout

- `scraper/` — headline collection (Stage 1)
- `annotate/` — annotation pipeline (Stage 2)
- `models/` — shared data-loading/splitting logic reused across Stage 3-5
  notebooks (tested — see `tests/test_data.py`)
- `data/raw/` — scraped, unlabeled headlines + data card
- `data/processed/` — annotated data (Stage 2) and final labeled dataset
- `notebooks/` — modeling and EDA (Stage 3+)
- `app/` — Streamlit demo (Stage 5)
