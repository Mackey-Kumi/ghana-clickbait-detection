# Kaggle workflow

This machine has no GPU (Intel UHD 620 integrated graphics only), so Stage 4's
DistilBERT fine-tuning runs remotely on a Kaggle T4 instead. Every experiment
here is a **script kernel**: pushed via the Kaggle CLI, run server-side,
polled for completion, then its log/output pulled back down. Pattern borrowed
from a previous project's `kaggle/` setup.

## One-time setup

1. Create a Kaggle account, then get an API token at kaggle.com/settings/api
   ("Create New Token"). Save it to `~/.kaggle/access_token` (this CLI version
   — 2.2.4 — doesn't use the older `kaggle.json` format).
2. `pip install kaggle` (not tracked in `requirements.txt` — this repo's own
   dependencies never need it; it's only used from the command line to drive
   remote training).
3. The `annotated_headlines` dataset needs to exist on Kaggle before any
   experiment can run — push it once (must `cd` into the directory first; a
   relative multi-segment path passed via `-p` hits a path-join bug on
   Windows in this CLI version):
   ```bash
   cd kaggle/datasets/annotated_headlines
   kaggle datasets create -p .
   ```

## Running an experiment

```bash
export PYTHONUTF8=1   # avoids a console encoding crash on Windows when pulling logs (headline text has heavy unicode)
cd kaggle/experiments/<name>
kaggle kernels push -p .
kaggle kernels status mackeykumi/<kernel-id>              # poll until COMPLETE or ERROR
kaggle kernels output mackeykumi/<kernel-id> -p ./output -o
```

The `<kernel-id>` is the `id` field in that experiment's `kernel-metadata.json`.

## Experiments

| Folder | Question it answered | Result |
|---|---|---|
| `01_finetune_distilbert` | Fine-tuned DistilBERT vs. Stage 3's TF-IDF+LR baseline, same seed=42 80/20 split, plus a held-out-outlet generalization check | Beats the baseline on every standard-split metric (accuracy 0.783 vs 0.737, macro F1 0.714 vs 0.647, Clickbait recall 0.744 vs 0.590). Generalizes much better to unseen clickbait-heavy outlets too (held-out Clickbait recall 0.736 vs baseline's 0.453). All 8 training runs (1 standard + 7 held-out-outlet) together took ~104 seconds on a single T4. See `notebooks/transformer.ipynb` for the full write-up. |

Kaggle's free-tier accelerators for this account: a single `NvidiaTeslaT4` via
`"machine_shape": "NvidiaTeslaT4"` in `kernel-metadata.json` was sufficient —
DistilBERT (66M params) fine-tuning on <1,000 short headlines doesn't need
the T4x2/dual-GPU setup a larger model would.
