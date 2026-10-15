# Failure Log

Things that went wrong during the project, what caused them, and what I did
about them. Ordered by project stage.

## Stage 1: Scraping

| Problem | Cause | Fix / decision |
|---|---|---|
| Myjoyonline and Citinewsroom stopped short of their headline targets | `/page/N/` pagination returned the same stories as page 1 for some categories (confirmed by fetching pages live) | Myjoyonline: collected page 1 of five categories instead. Citinewsroom: switched to the "news" category, which really paginates (checked 12 pages deep) |
| Graphic Online only yielded 35 headlines | Its category pages don't paginate and only two sections share a scrapable template | Accepted the cap and took more headlines from the other three mainstream outlets to keep 500/500. Documented in `data/raw/DATA_CARD.md` |
| Yen.com.gh listing pages returned no headlines | Listing pages are rendered client-side | Switched Yen to its XML sitemap plus a per-article fetch |
| ghgossip.com and ameyawdebrah.com could not be used | Both disallow AI crawlers in `robots.txt` | Excluded them rather than working around the block (ethical line) |
| Packages installed into the global Python by mistake | Ran `pip install` before creating the virtual environment | Restored the original global versions and moved all work into `.venv` |
| Console crashed printing headlines | Windows console encoding (cp1252) can't print curly quotes or the cedi sign | Wrote output to UTF-8 files instead of the console; set `PYTHONUTF8=1` where needed |

## Stage 2: Annotation

| Problem | Cause | Fix / decision |
|---|---|---|
| AI draft labels missed most clickbait (32 of 196) | The first codebook didn't cover decontextualised quotes, disturbing-topic headlines or vague hype adjectives | Reviewed all 1,000 drafts by hand (167 overrides) and revised the codebook three times |
| Inter-annotator agreement κ = 0.057 | The second annotator labelled without seeing the codebook, and used a much broader everyday meaning of "clickbait" (41.8% vs. 16.5%) | Reported as-is with a full explanation instead of re-running; it is a finding about how vague "clickbait" is without a written definition. Listed as a limitation |
| Second annotator's file was an Excel sheet, but the Kappa script only read CSV | Sent them an `.xlsx` with dropdowns to avoid typos | Added `.xlsx` support to `annotate/csv_io.py` and `annotate/kappa.py` |

## Stage 3: Baseline

| Problem | Cause | Fix / decision |
|---|---|---|
| Baseline looked good (82.3% accuracy) but caught only 10.3% of clickbait | ~80/20 class imbalance; the model learned to predict "Informative" for almost everything | Switched to `class_weight="balanced"` and made macro F1 and Clickbait recall the headline metrics |
| Top features included topic words (*mahama*, *npp*, *2026*) and a celebrity first name | The model partly learns topic/outlet vocabulary instead of clickbait style | Added the held-out-outlet test, which confirmed it (gossip-outlet Clickbait recall dropped 0.590 → 0.453) |
| Baseline misses "BREAKING" and other capitalisation signals | `TfidfVectorizer` lowercases text by default | Found during error analysis; documented as a design flaw, not fixed before submission |

## Stage 4: DistilBERT on Kaggle

| Problem | Cause | Fix / decision |
|---|---|---|
| No GPU on my laptop | Integrated graphics only | Trained on a free Kaggle T4 via the Kaggle CLI (`kaggle/README.md`) |
| `kaggle` command not found | Installed into a Scripts folder that wasn't on PATH | Called it by full path |
| `kaggle auth login` hung with no output | OAuth flow doesn't work in this terminal environment | Used an API token saved to `~/.kaggle/access_token` instead. The token is not in this repository |
| `kaggle datasets create -p kaggle/datasets/...` failed | Path-joining bug on Windows with multi-folder relative paths in this CLI version | `cd` into the folder first and use `-p .` |

## Stage 5: Zero-shot

| Problem | Cause | Fix / decision |
|---|---|---|
| Zero-shot model caught zero clickbait (recall 0.000 on every outlet) | The literal labels "clickbait"/"informative" don't work as NLI hypotheses | Added a second run with descriptive labels on the same test set: recall rose to 0.410. Both results reported |
| Pulling the kernel's output failed | Kaggle created the kernel under a slightly different slug (`zero-shot` vs. `zeroshot`) | Updated `kernel-metadata.json` to the real slug |
| No per-headline predictions saved for DistilBERT or zero-shot | Kaggle scripts only wrote metrics | Error analysis done on the baseline instead; listed as a limitation |

## Write-up

| Problem | Cause | Fix / decision |
|---|---|---|
| README stated DistilBERT's held-out Clickbait recall as 0.744 | Copied the random-split number instead of the held-out average | Corrected to 0.736 (matches `held_out_results.csv`) |
