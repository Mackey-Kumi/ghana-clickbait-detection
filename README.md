# Detecting Clickbait and Sensationalism in Ghanaian Online News Headlines

A research project comparing three modeling approaches — classical ML, a
fine-tuned transformer, and a zero-shot LLM — on a purpose-built,
human-annotated dataset of Ghanaian news headlines. DCIT 316 — Computational
Models for Social Media Mining, University of Ghana, 2025/2026.

Scoped as a research comparison, not a deployed product: the deliverable is
the dataset, the annotation methodology, and the model comparison, not a
web app.

## Results at a glance

Same 1,000-headline dataset, same seed=42 80/20 test split, all three models:

| | Accuracy | Macro F1 | Clickbait Precision | Clickbait Recall |
|---|---|---|---|---|
| Baseline (TF-IDF + Logistic Regression) | 0.737 | 0.647 | 0.390 | 0.590 |
| **Fine-tuned DistilBERT** | **0.783** | **0.714** | **0.468** | **0.744** |
| Zero-shot (`bart-large-mnli`, literal labels) | 0.798* | 0.444 | 0.000 | 0.000 |
| Zero-shot (`bart-large-mnli`, descriptive labels) | 0.788 | 0.651 | 0.457 | 0.410 |

\* Zero-shot's raw accuracy is a majority-class artifact on this imbalanced
dataset, not evidence of real classification skill — see
`notebooks/zeroshot.ipynb`.

Fine-tuned DistilBERT wins outright, and also generalizes best to headlines
from outlets it never trained on (held-out-outlet Clickbait recall 0.736 vs.
the baseline's 0.453). Full methodology and discussion in each stage's
notebook, linked below.

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
Full source list, collection method, and known limitations: `data/raw/DATA_CARD.md`.

## Stage 2 — Annotation

`data/processed/pre_labels.csv` (all 1,000 headlines) and
`data/processed/second_annotator_subset.csv` (the 250-headline blind subset)
are already generated. Codebook: `docs/ANNOTATION_CODEBOOK.md`.

Send a second annotator `second_annotator_subset.xlsx`, not the `.csv` —
same 250 headlines, but the `label` column has a dropdown (Clickbait /
Informative / Ambiguous) instead of requiring them to type the label by hand.

```bash
python -m annotate.verify              # verification pass -- resumable, stop/start anytime
```

Once the second annotator returns their file filled in:

```bash
python -m annotate.kappa path/to/their-completed-subset.csv
python -m annotate.merge_final         # only after the verify.py pass is 100% complete
```

Output: `data/processed/annotated_headlines.csv` — 1,000 labeled headlines
(Clickbait/Informative/Ambiguous). Full annotation methodology, override
rate, and inter-annotator agreement: `data/raw/DATA_CARD.md`.

## Stage 3 — Baseline model

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/baseline.ipynb
```

TF-IDF (unigrams+bigrams) + Logistic Regression, class-balanced. Reuses
`models.data.load_labeled_dataset()`/`make_train_test_split()` (seed 42) so
every stage evaluates on the identical test set. Includes a held-out-outlet
generalization check (train on 6 outlets, test on the 7th) alongside the
standard 80/20 split, and a top-features table.

## Stage 4 — Fine-tuned DistilBERT

This machine has no GPU, so training runs remotely on a free Kaggle T4 —
see `kaggle/README.md` for the full push/poll/pull workflow and how to
re-run it. Results are already pulled down to
`kaggle/experiments/01_finetune_distilbert/output/`; to view the write-up
without re-running anything:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/transformer.ipynb
```

## Stage 5 — Zero-shot LLM classification

Same remote-Kaggle pattern as Stage 4, inference only (no training):

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/zeroshot.ipynb
```

`facebook/bart-large-mnli`, no fine-tuning. Includes a robustness check on
candidate-label phrasing — see `kaggle/README.md`'s experiment table and
`notebooks/zeroshot.ipynb` for the full write-up.

## Error analysis

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/error_analysis.ipynb
```

Every headline the baseline gets wrong on the shared test set, broken down by
outlet, with a summary of the error patterns. Discussed in the manuscript's
Section 6.

## Research documentation

| Document | Contents |
|---|---|
| `report/` | The research manuscript (PDF) |
| `data/raw/DATA_CARD.md` | Sources, collection method, label distribution, annotation process, known limitations |
| `docs/ANNOTATION_CODEBOOK.md` | Labelling guidelines, including the three revisions |
| `docs/MODEL_CARD.md` | All three models: training setup, metrics, intended use, failure modes |
| `docs/LITERATURE_MATRIX.md` | Related work and how each paper shaped a decision here |
| `docs/ETHICS.md` | Scraping ethics, annotator anonymity, data access, responsible use |
| `docs/AI_USE_DISCLOSURE.md` | Where AI was used and how its output was verified |
| `docs/FAILURE_LOG.md` | What went wrong at each stage and how it was handled |
| `docs/REPRODUCIBILITY.md` | Reproducibility checklist and full re-run steps |

## Data access

Everything needed to reproduce the results is in this repository: the scraped
headlines (`data/raw/`) and all labels (`data/processed/`). The data is public
news headlines and labels derived from them, with no personal data, restricted
datasets or credentials. Re-running the scraper is optional and will give
different headlines, since the sites change daily. Check each site's current
`robots.txt` first. See `docs/ETHICS.md`.

## Project layout

- `scraper/` — headline collection (Stage 1)
- `annotate/` — annotation pipeline (Stage 2)
- `models/` — shared data-loading/splitting logic reused across Stage 3-5
  notebooks (tested — see `tests/test_data.py`)
- `kaggle/` — remote GPU/inference via the Kaggle CLI (Stage 4-5; see
  `kaggle/README.md`)
- `data/raw/` — scraped, unlabeled headlines + data card
- `data/processed/` — annotated data (Stage 2) and final labeled dataset
- `notebooks/` — modeling, evaluation, and write-up for each stage
- `docs/` — codebook, model card, literature matrix, ethics, AI-use
  disclosure, failure log, reproducibility checklist
- `report/` — research manuscript
- `tests/` — unit tests for the scraping/annotation/data-loading pipeline

## License

MIT — see `LICENSE`.
