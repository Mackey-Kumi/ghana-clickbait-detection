# Model Card

Covers the three models compared in this project. The fine-tuned DistilBERT
model is the best-performing one and the main subject of this card.

## Model details

| | Baseline | Fine-tuned transformer | Zero-shot |
|---|---|---|---|
| Model | TF-IDF (unigrams + bigrams, min_df=2) + Logistic Regression, `class_weight="balanced"` | `distilbert-base-uncased`, class-weighted cross-entropy | `facebook/bart-large-mnli`, no training |
| Training | 792 headlines, local CPU | 792 headlines, Kaggle T4 GPU, 4 epochs, batch 16, lr 2e-5, weight decay 0.01, max length 64 | none |
| Code | `notebooks/baseline.ipynb` | `kaggle/experiments/01_finetune_distilbert/` | `kaggle/experiments/02_zeroshot_classification/` |
| Seed | 42 | 42 | n/a (deterministic inference) |

The trained model weights are **not** saved or distributed. Only metrics,
confusion matrices and logs are kept. The baseline can be retrained in
seconds from the notebook; DistilBERT can be retrained on Kaggle in about two
minutes using the script.

## Intended use

Research comparison only: measuring how well different approaches detect
clickbait in Ghanaian English-language news headlines. A possible downstream
use would be a reader-facing *warning* label. It is **not** intended for
blocking, ranking or penalising content or outlets.

## Training and evaluation data

`data/processed/annotated_headlines.csv`: 1,000 headlines from seven Ghanaian
outlets, scraped 25 August 2026 and labelled by one primary annotator under
`docs/ANNOTATION_CODEBOOK.md`. The 10 Ambiguous headlines were excluded,
leaving 990 (794 Informative, 196 Clickbait). Stratified 80/20 split, seed 42:
792 train, 198 test (159 Informative, 39 Clickbait). See `data/raw/DATA_CARD.md`.

## Metrics (same 198-headline test set)

| Model | Accuracy | Macro F1 | Clickbait precision | Clickbait recall |
|---|---|---|---|---|
| Baseline | 0.737 | 0.647 | 0.390 | 0.590 |
| **DistilBERT** | **0.783** | **0.714** | **0.468** | **0.744** |
| Zero-shot, literal labels | 0.798 | 0.444 | 0.000 | 0.000 |
| Zero-shot, descriptive labels | 0.788 | 0.651 | 0.457 | 0.410 |

Held-out-outlet test (train on six outlets, test on the seventh), averaged
over the three gossip outlets: baseline Clickbait recall 0.453, DistilBERT
0.736.

Accuracy is not a reliable metric here because the data is ~80% Informative:
the zero-shot model with literal labels reaches the highest accuracy while
catching no clickbait at all.

## Limitations and known failure modes

- **False alarms on gossip-site headlines.** DistilBERT flags 33 of 159
  informative test headlines as clickbait (precision 0.468). The error
  analysis (`notebooks/error_analysis.ipynb`) shows the baseline's false
  alarms are almost all factual celebrity/entertainment headlines and short
  crime headlines. Roughly half of what DistilBERT flags is real clickbait.
- **Misses subtle clickbait.** Vague hype ("fine figure", "plush") and
  decontextualised quotes are the hardest cases.
- **Topic confound.** Clickbait is concentrated in entertainment news and
  politics is almost always informative, so models can partly learn topic
  instead of clickbait style.
- **Small test set.** Only 39 Clickbait test headlines; no confidence
  intervals or repeated seeds.
- **Single annotator's ground truth.** Inter-annotator agreement with an
  untrained second annotator was κ = 0.057.
- **English only**, headlines only (no article bodies), one-day snapshot.

## Ethical considerations

A "clickbait" label is a judgement about headline style, not a claim that a
story is false, and the results must not be read as a ranking of outlets'
trustworthiness. See `docs/ETHICS.md`.
