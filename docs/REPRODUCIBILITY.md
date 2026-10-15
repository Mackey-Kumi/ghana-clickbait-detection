# Reproducibility Checklist

| Item | Status | Where |
|---|---|---|
| Dependencies pinned to exact versions | ⚠️ partly | `requirements.txt` pins every local dependency. The Kaggle scripts use Kaggle's pre-installed libraries (not pinned); the logs record PyTorch 2.10.0+cu128 |
| Random seeds fixed | ✅ | Seed 42 for every train/test split and model (`models/data.py`, notebooks, Kaggle scripts) |
| Same test set for every model | ✅ | All stages call `models.data.make_train_test_split(df, test_size=0.2, seed=42)`; covered by `tests/test_data.py` |
| Raw data included | ✅ | `data/raw/*.csv`, `data/raw/headlines_combined.csv` |
| Labelled data included | ✅ | `data/processed/annotated_headlines.csv` (final), plus `pre_labels.csv`, `verified_labels.csv` and the second annotator's file |
| Data card | ✅ | `data/raw/DATA_CARD.md` |
| Annotation guidelines | ✅ | `docs/ANNOTATION_CODEBOOK.md` |
| Notebooks with saved outputs | ✅ | `notebooks/baseline.ipynb`, `transformer.ipynb`, `zeroshot.ipynb`, `error_analysis.ipynb` |
| Saved metrics and figures | ✅ | `kaggle/experiments/*/output/` (metrics JSON/CSV, logs); `notebooks/*.png` (confusion matrices) |
| Model card | ✅ | `docs/MODEL_CARD.md` |
| Unit tests | ✅ | `tests/` (`python -m pytest`) |
| GPU steps reproducible | ✅ | Full Kaggle push/poll/pull workflow in `kaggle/README.md` |
| Trained model weights | ❌ not saved | Baseline retrains in seconds; DistilBERT in ~2 minutes on a Kaggle T4 |
| Per-headline predictions for DistilBERT/zero-shot | ❌ not saved | Only metrics and confusion matrices were written by the Kaggle scripts |
| Scraping re-run gives identical data | ❌ not expected | News sites change daily; the scraped snapshot (25 Aug 2026) is committed so later stages don't depend on re-scraping |
| No secrets or restricted data committed | ✅ | Full git history checked before the repository was made public |
| Failure log | ✅ | `docs/FAILURE_LOG.md` |
| Ethics statement and AI-use disclosure | ✅ | `docs/ETHICS.md`, `docs/AI_USE_DISCLOSURE.md` |

## Re-running everything from scratch

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt     # Windows; use .venv/bin/pip elsewhere
python -m pytest                                   # unit tests
jupyter nbconvert --to notebook --execute --inplace notebooks/baseline.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/error_analysis.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/transformer.ipynb   # reads saved Kaggle results
jupyter nbconvert --to notebook --execute --inplace notebooks/zeroshot.ipynb      # reads saved Kaggle results
```

To retrain DistilBERT or re-run zero-shot on a GPU, follow `kaggle/README.md`.
To re-scrape (optional, results will differ): `python -m scraper.scrape`.
