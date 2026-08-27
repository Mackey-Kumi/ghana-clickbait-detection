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

## Stage 4 — Fine-tuned DistilBERT

This machine has no GPU, so training runs remotely on a free Kaggle T4 —
see `kaggle/README.md` for the full push/poll/pull workflow and how to
re-run it. Results are already pulled down to
`kaggle/experiments/01_finetune_distilbert/output/`; to view the write-up
without re-running anything:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/transformer.ipynb
```

Beats the Stage 3 baseline on every metric (accuracy 0.783 vs 0.737, macro F1
0.714 vs 0.647, Clickbait recall 0.744 vs 0.590) and generalizes much better
to unseen clickbait-heavy outlets in the held-out-outlet check (Clickbait
recall 0.736 vs the baseline's 0.453).

## Stage 5 — Zero-shot LLM classification

Same remote-Kaggle pattern as Stage 4, inference only (no training):

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/zeroshot.ipynb
```

`facebook/bart-large-mnli`, no fine-tuning. The proposal's literal candidate
labels (`"clickbait"`/`"informative"`) collapse almost completely (Clickbait
precision/recall both 0.000) — but that's substantially a label-phrasing
artifact, not a hard capability ceiling: richer descriptive candidate labels
on the identical test set lift Clickbait recall to 0.410 and macro F1 to
0.651 (essentially tied with the Stage 3 baseline), while still falling
short of fine-tuned DistilBERT (0.714) either way — the annotated dataset
and fine-tuning effort demonstrably earn their keep. See
`kaggle/README.md`'s experiment table and `notebooks/zeroshot.ipynb` for the
full write-up.

The Streamlit demo app (the proposal's other Stage 5 deliverable) is
deferred for now — it's a product/polish piece that doesn't feed the
research comparison, unlike the model itself.

## Project layout

- `scraper/` — headline collection (Stage 1)
- `annotate/` — annotation pipeline (Stage 2)
- `models/` — shared data-loading/splitting logic reused across Stage 3-5
  notebooks (tested — see `tests/test_data.py`)
- `kaggle/` — remote GPU/inference via the Kaggle CLI (Stage 4-5; see
  `kaggle/README.md`)
- `data/raw/` — scraped, unlabeled headlines + data card
- `data/processed/` — annotated data (Stage 2) and final labeled dataset
- `notebooks/` — modeling and EDA (Stage 3+)
- `app/` — Streamlit demo (deferred — see Stage 5 above)
