"""
DCIT 316 Stage 4: fine-tune distilbert-base-uncased on the annotated
Ghanaian news headline dataset (Clickbait/Informative; Ambiguous excluded
from training, matching Stage 3). Runs on a single Kaggle T4.

Same stratified 80/20 split (seed=42) as Stage 3's TF-IDF+LR baseline, for a
fair comparison, plus a held-out-outlet generalization check (retrain once
per outlet, holding that outlet's headlines out as the test set) -- the same
check that revealed outlet-vocabulary memorization in the baseline.

Class-imbalance handling mirrors Stage 3's class_weight="balanced": a
weighted cross-entropy loss computed from each run's own training split.

Results (classification report, confusion matrix, held-out-outlet table)
are written to /kaggle/working/ for pulling back with `kaggle kernels output`.
"""

import json
import os
import time

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from torch.utils.data import Dataset
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast, Trainer, TrainingArguments

torch.manual_seed(42)

assert torch.cuda.is_available(), "No GPU attached -- check the notebook's accelerator setting"
print(f"GPU: {torch.cuda.get_device_properties(0).name}")
print(f"PyTorch: {torch.__version__}")

# ---------------------------------------------------------------------------
# 1. Data -- same loading/splitting logic as models.data, reimplemented here
#    since the local package isn't available inside the Kaggle kernel.
# ---------------------------------------------------------------------------
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

LABEL2ID = {"Informative": 0, "Clickbait": 1}
ID2LABEL = {v: k for k, v in LABEL2ID.items()}

train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["label"])
print(f"Standard split -- train: {len(train_df)}, test: {len(test_df)}")

MODEL_NAME = "distilbert-base-uncased"
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)


class HeadlineDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=64):
        self.encodings = tokenizer(list(texts), truncation=True, padding=True, max_length=max_length)
        self.labels = [LABEL2ID[label] for label in labels]

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="macro", zero_division=0)
    cb_precision, cb_recall, cb_f1, _ = precision_recall_fscore_support(
        labels, preds, labels=[LABEL2ID["Clickbait"]], average="macro", zero_division=0
    )
    return {
        "accuracy": (preds == labels).mean(),
        "macro_f1": f1,
        "macro_precision": precision,
        "macro_recall": recall,
        "clickbait_precision": cb_precision,
        "clickbait_recall": cb_recall,
        "clickbait_f1": cb_f1,
    }


def make_weighted_trainer_class(class_weights_tensor):
    class WeightedTrainer(Trainer):
        def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
            labels = inputs.pop("labels")
            outputs = model(**inputs)
            logits = outputs.logits
            loss_fct = torch.nn.CrossEntropyLoss(weight=class_weights_tensor.to(logits.device))
            loss = loss_fct(logits, labels)
            return (loss, outputs) if return_outputs else loss

    return WeightedTrainer


def train_and_evaluate(train_frame, test_frame, run_name, output_subdir):
    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.array([0, 1]),
        y=[LABEL2ID[label] for label in train_frame["label"]],
    )
    class_weights_tensor = torch.tensor(class_weights, dtype=torch.float)
    print(f"[{run_name}] class weights (Informative, Clickbait): {class_weights}")

    model = DistilBertForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=2, id2label=ID2LABEL, label2id=LABEL2ID
    )
    train_dataset = HeadlineDataset(train_frame["headline_text"], train_frame["label"], tokenizer)
    test_dataset = HeadlineDataset(test_frame["headline_text"], test_frame["label"], tokenizer)

    args = TrainingArguments(
        output_dir=f"/kaggle/working/{output_subdir}",
        num_train_epochs=4,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        learning_rate=2e-5,
        weight_decay=0.01,
        save_strategy="no",
        logging_steps=10,
        report_to="none",
        seed=42,
    )
    trainer_cls = make_weighted_trainer_class(class_weights_tensor)
    trainer = trainer_cls(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics,
    )

    start = time.time()
    trainer.train()
    elapsed = time.time() - start
    metrics = trainer.evaluate()
    metrics["train_time_seconds"] = elapsed
    print(f"[{run_name}] metrics: {metrics}")
    return trainer, metrics


# ---------------------------------------------------------------------------
# 2. Standard 80/20 evaluation
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STANDARD 80/20 SPLIT")
print("=" * 70)
main_trainer, main_metrics = train_and_evaluate(train_df, test_df, "standard_split", "standard")

test_dataset_for_report = HeadlineDataset(test_df["headline_text"], test_df["label"], tokenizer)
preds_output = main_trainer.predict(test_dataset_for_report)
y_pred = np.argmax(preds_output.predictions, axis=-1)
y_true = [LABEL2ID[label] for label in test_df["label"]]

report = classification_report(y_true, y_pred, target_names=["Informative", "Clickbait"], digits=3, output_dict=True)
print(classification_report(y_true, y_pred, target_names=["Informative", "Clickbait"], digits=3))
cm = confusion_matrix(y_true, y_pred).tolist()
print("Confusion matrix (rows=true, cols=pred, order=[Informative, Clickbait]):", cm)

# ---------------------------------------------------------------------------
# 3. Held-out-outlet generalization check
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("HELD-OUT-OUTLET CHECK")
print("=" * 70)
held_out_results = []
for outlet in sorted(df["outlet"].unique()):
    train_ho = df[df["outlet"] != outlet].reset_index(drop=True)
    test_ho = df[df["outlet"] == outlet].reset_index(drop=True)
    if train_ho["label"].nunique() < 2:
        print(f"Skipping {outlet}: training set missing a class")
        continue

    _, ho_metrics = train_and_evaluate(train_ho, test_ho, f"held_out_{outlet}", f"ho_{outlet}")
    held_out_results.append(
        {
            "held_out_outlet": outlet,
            "source_style": test_ho["source_style"].iloc[0],
            "n_test": len(test_ho),
            "accuracy": round(float(ho_metrics["eval_accuracy"]), 3),
            "macro_f1": round(float(ho_metrics["eval_macro_f1"]), 3),
            "clickbait_recall": round(float(ho_metrics["eval_clickbait_recall"]), 3),
        }
    )

held_out_df = pd.DataFrame(held_out_results)
print(held_out_df)

# ---------------------------------------------------------------------------
# 4. Write results for pulling back with `kaggle kernels output`
# ---------------------------------------------------------------------------
results = {
    "standard_split": {
        "classification_report": report,
        "confusion_matrix": cm,
        "accuracy": float(main_metrics["eval_accuracy"]),
        "macro_f1": float(main_metrics["eval_macro_f1"]),
        "clickbait_precision": float(main_metrics["eval_clickbait_precision"]),
        "clickbait_recall": float(main_metrics["eval_clickbait_recall"]),
        "train_time_seconds": main_metrics["train_time_seconds"],
    },
    "held_out_outlet": held_out_results,
}
with open("/kaggle/working/results.json", "w") as f:
    json.dump(results, f, indent=2)

held_out_df.to_csv("/kaggle/working/held_out_results.csv", index=False)

print("\nDONE. Results written to /kaggle/working/results.json and held_out_results.csv")
