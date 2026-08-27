"""
DCIT 316 Stage 5: zero-shot LLM classification via facebook/bart-large-mnli
(Hugging Face zero-shot-classification pipeline, no task-specific training)
-- tests whether a pretrained model can perform the clickbait/informative
task out of the box, and how much value Stage 2's annotated dataset plus
Stage 3/4's supervised training actually added.

Evaluated two ways:
  1. The same seed=42 80/20 test split used by Stage 3 (baseline) and
     Stage 4 (DistilBERT), for a direct, fair 3-way comparison.
  2. The full 990-headline dataset, broken down by outlet -- since this
     model was never trained on any of our data, this is a natural "unseen
     everything" generalization baseline to compare against Stage 3/4's
     held-out-outlet numbers.

Runs on a single Kaggle T4. Inference only, no training.
"""

import json
import os
import time

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from transformers import pipeline

assert torch.cuda.is_available(), "No GPU attached -- check the notebook's accelerator setting"
print(f"GPU: {torch.cuda.get_device_properties(0).name}")
print(f"PyTorch: {torch.__version__}")

DATA_CANDIDATES = [
    "/kaggle/input/dcit316-annotated-headlines/annotated_headlines.csv",
    "/kaggle/input/datasets/mackeykumi/dcit316-annotated-headlines/annotated_headlines.csv",
]


def load_data():
    for path in DATA_CANDIDATES:
        if os.path.exists(path):
            return pd.read_csv(path)
    raise RuntimeError(f"Could not find annotated_headlines.csv in any of: {DATA_CANDIDATES}")


df = load_data()
df = df[df["label"] != "Ambiguous"].reset_index(drop=True)
print(f"Total labeled headlines (Ambiguous excluded): {len(df)}")
print(df["label"].value_counts())

# Same split as Stage 3/4 -- for the direct 3-way comparison. Zero-shot needs
# no training data, so only the test half of this split is used below.
_, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["label"])
print(f"Standard-split test set: {len(test_df)}")

MODEL_NAME = "facebook/bart-large-mnli"
CANDIDATE_LABELS = ["clickbait", "informative"]
HYPOTHESIS_TEMPLATE = "This news headline is {}."
LABEL_MAP = {"clickbait": "Clickbait", "informative": "Informative"}

classifier = pipeline("zero-shot-classification", model=MODEL_NAME, device=0, batch_size=16)


def classify(headlines):
    start = time.time()
    outputs = classifier(list(headlines), candidate_labels=CANDIDATE_LABELS, hypothesis_template=HYPOTHESIS_TEMPLATE)
    elapsed = time.time() - start
    if isinstance(outputs, dict):  # a single input isn't wrapped in a list
        outputs = [outputs]
    preds = [LABEL_MAP[o["labels"][0]] for o in outputs]
    scores = [o["scores"][0] for o in outputs]
    return preds, scores, elapsed


# ---------------------------------------------------------------------------
# 1. Standard 80/20 test-set evaluation (matches Stage 3/4)
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STANDARD 80/20 SPLIT (test set only -- zero-shot needs no training data)")
print("=" * 70)
y_pred, pred_scores, elapsed = classify(test_df["headline_text"])
y_true = test_df["label"].tolist()

report = classification_report(y_true, y_pred, labels=["Informative", "Clickbait"], digits=3, output_dict=True)
print(classification_report(y_true, y_pred, labels=["Informative", "Clickbait"], digits=3))
cm = confusion_matrix(y_true, y_pred, labels=["Informative", "Clickbait"]).tolist()
print("Confusion matrix (rows=true, cols=pred, order=[Informative, Clickbait]):", cm)

accuracy = float((np.array(y_true) == np.array(y_pred)).mean())
_, _, macro_f1, _ = precision_recall_fscore_support(
    y_true, y_pred, labels=["Informative", "Clickbait"], average="macro", zero_division=0
)
cb_precision, cb_recall, cb_f1, _ = precision_recall_fscore_support(
    y_true, y_pred, labels=["Clickbait"], average="macro", zero_division=0
)
print(f"Inference time for {len(test_df)} headlines: {elapsed:.1f}s")

# ---------------------------------------------------------------------------
# 1b. Robustness check: is the near-zero Clickbait recall above a genuine
#     zero-shot capability gap, or an artifact of "clickbait"/"informative"
#     being weak bare-word NLI hypotheses? Bare slang terms like "clickbait"
#     may carry little entailment signal on their own. Re-run the same test
#     set with richer, more descriptive candidate-label phrasing.
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("ROBUSTNESS CHECK: richer candidate-label phrasing, same test set")
print("=" * 70)
RICH_CANDIDATE_LABELS = [
    "a sensationalized clickbait headline designed to provoke curiosity",
    "a factual, informative news headline",
]
RICH_LABEL_MAP = {
    "a sensationalized clickbait headline designed to provoke curiosity": "Clickbait",
    "a factual, informative news headline": "Informative",
}


def classify_rich(headlines):
    start = time.time()
    outputs = classifier(list(headlines), candidate_labels=RICH_CANDIDATE_LABELS, hypothesis_template="This is {}.")
    elapsed = time.time() - start
    if isinstance(outputs, dict):
        outputs = [outputs]
    preds = [RICH_LABEL_MAP[o["labels"][0]] for o in outputs]
    return preds, elapsed


y_pred_rich, elapsed_rich = classify_rich(test_df["headline_text"])
report_rich = classification_report(
    y_true, y_pred_rich, labels=["Informative", "Clickbait"], digits=3, output_dict=True
)
print(classification_report(y_true, y_pred_rich, labels=["Informative", "Clickbait"], digits=3))
cm_rich = confusion_matrix(y_true, y_pred_rich, labels=["Informative", "Clickbait"]).tolist()
print("Confusion matrix (rich labels):", cm_rich)

accuracy_rich = float((np.array(y_true) == np.array(y_pred_rich)).mean())
_, _, macro_f1_rich, _ = precision_recall_fscore_support(
    y_true, y_pred_rich, labels=["Informative", "Clickbait"], average="macro", zero_division=0
)
cb_precision_rich, cb_recall_rich, _, _ = precision_recall_fscore_support(
    y_true, y_pred_rich, labels=["Clickbait"], average="macro", zero_division=0
)
print(f"Inference time for {len(test_df)} headlines (rich labels): {elapsed_rich:.1f}s")

# ---------------------------------------------------------------------------
# 2. Per-outlet breakdown on the FULL dataset -- zero-shot never trained on
#    any of it, so this is a natural "unseen everything" generalization view
#    to compare against Stage 3/4's held-out-outlet numbers.
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PER-OUTLET BREAKDOWN (full dataset, since nothing was trained on)")
print("=" * 70)
full_pred, full_scores, full_elapsed = classify(df["headline_text"])
df_eval = df.copy()
df_eval["pred"] = full_pred
print(f"Inference time for all {len(df)} headlines: {full_elapsed:.1f}s")

per_outlet_results = []
for outlet in sorted(df_eval["outlet"].unique()):
    subset = df_eval[df_eval["outlet"] == outlet]
    acc = float((subset["label"] == subset["pred"]).mean())
    _, _, f1, _ = precision_recall_fscore_support(
        subset["label"], subset["pred"], labels=["Informative", "Clickbait"], average="macro", zero_division=0
    )
    _, cb_rec, _, _ = precision_recall_fscore_support(
        subset["label"], subset["pred"], labels=["Clickbait"], average="macro", zero_division=0
    )
    per_outlet_results.append(
        {
            "outlet": outlet,
            "source_style": subset["source_style"].iloc[0],
            "n": len(subset),
            "accuracy": round(acc, 3),
            "macro_f1": round(float(f1), 3),
            "clickbait_recall": round(float(cb_rec), 3),
        }
    )

per_outlet_df = pd.DataFrame(per_outlet_results)
print(per_outlet_df)

# ---------------------------------------------------------------------------
# 3. Write results for pulling back with `kaggle kernels output`
# ---------------------------------------------------------------------------
results = {
    "model": MODEL_NAME,
    "hypothesis_template": HYPOTHESIS_TEMPLATE,
    "standard_split": {
        "classification_report": report,
        "confusion_matrix": cm,
        "accuracy": accuracy,
        "macro_f1": float(macro_f1),
        "clickbait_precision": float(cb_precision),
        "clickbait_recall": float(cb_recall),
        "inference_time_seconds": elapsed,
    },
    "standard_split_rich_labels": {
        "candidate_labels": RICH_CANDIDATE_LABELS,
        "classification_report": report_rich,
        "confusion_matrix": cm_rich,
        "accuracy": accuracy_rich,
        "macro_f1": float(macro_f1_rich),
        "clickbait_precision": float(cb_precision_rich),
        "clickbait_recall": float(cb_recall_rich),
        "inference_time_seconds": elapsed_rich,
    },
    "per_outlet": per_outlet_results,
}
with open("/kaggle/working/results.json", "w") as f:
    json.dump(results, f, indent=2)

per_outlet_df.to_csv("/kaggle/working/per_outlet_results.csv", index=False)

print("\nDONE. Results written to /kaggle/working/results.json and per_outlet_results.csv")
