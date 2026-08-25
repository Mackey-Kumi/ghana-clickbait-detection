# Annotation Pipeline — Design Spec

Date: 2026-08-25
Stage: DCIT 316 project, Stage 2 (Annotation)
Source requirements: `end-of-sem-research-writeup.pdf` (project proposal, §3.2/3.3),
`docs/superpowers/specs/2026-08-25-headline-scraper-design.md` (Stage 1 — produced
the 1,000-headline `data/raw/headlines_combined.csv` this stage annotates)

## Context

Stage 1 produced 1,000 unlabeled headlines across 7 outlets. This stage assigns each
one a `Clickbait` / `Informative` / `Ambiguous` label. Per the proposal's ethics
section (AI use must be disclosed with specifics on what was generated vs.
independently authored), this stage uses a disclosed AI-assisted workflow rather
than either pure manual labeling or pure automated labeling:

1. Claude pre-labels all 1,000 headlines (a real per-headline judgment pass against
   a written codebook, not a keyword heuristic).
2. The primary human annotator (the project owner) reviews every pre-label via a
   CLI tool and can accept or override each one. This produces the actual ground
   truth — Claude's pass is a draft, not the answer.
3. A second, independent annotator blind-labels a 250-headline subset (no exposure
   to Claude's labels or the primary annotator's corrections) for Cohen's Kappa.

This must be disclosed in the paper's methodology/ethics section: which model
pre-labeled, that every label was human-reviewable and overridable, and the
override rate as a reported statistic.

## Codebook

`docs/ANNOTATION_CODEBOOK.md` formalizes the schema already sketched in the
proposal:

- **Clickbait** — deliberate curiosity gaps, emotional manipulation, vague
  references, excessive capitalisation, or false urgency used to generate clicks
  rather than inform.
- **Informative** — communicates the substance of the story clearly, without
  manufactured emotional hooks.
- **Ambiguous** — doesn't cleanly fit either — set aside, excluded from model
  training, but kept and reported as a measure of annotation difficulty.

Six Ghana-specific signal categories from the proposal, each with 2-3 example
phrases, used identically by Claude's pre-labeling pass, the primary annotator,
and (via the codebook, not the tool) the second annotator: excessive
capitalisation, vague celebrity references, curiosity-gap phrasing, false urgency
markers, emotional bait, incomplete enumeration.

## Architecture

```
docs/ANNOTATION_CODEBOOK.md
annotate/
├── __init__.py
├── csv_io.py              # shared read/write helpers (mirrors scraper/utils.py's role)
├── build_pre_label_template.py   # data/raw/headlines_combined.csv -> data/processed/pre_labels.csv (empty ai_label/ai_rationale columns)
├── apply_labels.py        # merges a batch of {url: (label, rationale)} into pre_labels.csv, keyed by url
├── verify.py               # interactive CLI: primary annotator accepts/overrides each pre-label
├── sampling.py             # stratified_sample() -- pure function, outlet-proportional
├── export_second_annotator.py   # builds the blind 250-headline subset + private id->url mapping
├── kappa.py                 # cohens_kappa() -- pure function -- + CLI to merge second annotator's completed file and report
└── merge_final.py           # verified_labels.csv -> data/processed/annotated_headlines.csv
data/processed/
├── pre_labels.csv                    # url, outlet, source_style, headline_text, ai_label, ai_rationale
├── verified_labels.csv               # + human_label, overridden (bool) -- written incrementally by verify.py
├── second_annotator_subset.csv       # id (H001-H250), headline_text, label (blank) -- SHARED with 2nd annotator
├── second_annotator_mapping.csv      # id, url, outlet, source_style -- NOT shared, used only to merge their results back
└── annotated_headlines.csv           # final: url, outlet, source_style, headline_text, label
```

**Anonymization for the second annotator:** their file must not contain `url`
(the domain name alone reveals the outlet, e.g. `ghpage.com` vs `graphic.com.gh`,
which could bias judgment toward "this outlet is the clickbait one") or `outlet`.
It gets only an opaque `id` and the headline text. The `id -> url` mapping used to
merge their completed labels back stays private to the project owner.

**Why `url` is the join key everywhere else:** Stage 1 confirmed zero duplicate
URLs across all 7 outlets, so it's already a reliable natural key — no synthetic
id needed except for the deliberately-anonymized second-annotator file.

## Pre-labeling mechanism

`build_pre_label_template.py` creates the empty-label CSV. Claude then works
through it in batches (e.g. 100-150 rows at a time): reads each headline's text,
judges it against the codebook, and calls `apply_labels.py` with the batch's
`{url: (label, rationale)}` results to persist them. This is a genuine per-item
reasoning pass done directly in the session, not a scripted classifier — there is
no "run this file and it labels everything" automation, by design, since the
judgment quality is the point.

## `verify.py` (primary annotator CLI)

For each row in `pre_labels.csv` not yet in `verified_labels.csv`: print the
headline text, Claude's `ai_label` and `ai_rationale` (no outlet/url shown, to
keep the human's judgment focused on the text itself, same as the second
annotator's task). Keys: `c`/`i`/`a` to set the label explicitly, Enter to accept
the AI's suggested label, `q` to save and quit. Every decision is appended to
`verified_labels.csv` immediately (not batched), so the process is resumable —
re-running `verify.py` picks up from the first unverified row. At the end (or via
a `--stats` flag), prints total reviewed, override count, and override rate.

## Second annotator subset

`sampling.py`'s `stratified_sample(outlet_counts: dict[str, int], target_total: int) -> dict[str, int]`
takes each outlet's headline count (from Stage 1: myjoyonline 155, graphic 35,
citinewsroom 155, gna 155, ghpage 167, zionfelix 167, yen 166) and a target of
250, returns each outlet's proportional sample size, rounded so the sizes sum to
exactly 250. `export_second_annotator.py` uses this to sample 250 headlines
proportionally across outlets, assigns each an opaque `id` (`H001`-`H250`), and
writes the two files described above.

## Cohen's Kappa

`kappa.py`'s `cohens_kappa(labels_a: list[str], labels_b: list[str]) -> float`
is a standalone implementation (no new dependency — the formula is
`(po - pe) / (1 - pe)` from each rater's label frequencies) computed over all
three categories (Clickbait/Informative/Ambiguous), since the Ambiguous rate
itself is a reported difficulty measure per the proposal. The module's CLI takes
the second annotator's completed subset file, joins it back to
`verified_labels.csv` via `second_annotator_mapping.csv`, and prints the Kappa
score plus a simple agreement/disagreement breakdown by label pair.

## Final merge

`merge_final.py` reformats `verified_labels.csv` (url, outlet, source_style,
headline_text, human_label) into `data/processed/annotated_headlines.csv` with
column `label`. Ambiguous rows are kept (not dropped) — Stage 3's modeling code
filters them out at load time, consistent with the proposal's "set aside and
excluded from training" instruction while preserving them for the difficulty
analysis.

## Testing approach

Pure, unit-testable logic: `stratified_sample()` (given outlet counts and a
target, sizes sum exactly to target, no outlet gets 0 if its count > 0),
`cohens_kappa()` (known small examples with hand-computable expected values,
including the perfect-agreement and chance-agreement edge cases), and the
`apply_labels.py` merge-by-url logic. `verify.py`'s interactive loop is I/O-heavy
like Stage 1's `scrape.py::run()` — verified by manual walkthrough, not automated
tests, consistent with how Stage 1 handled its CLI wrapper.

## Ethics artifact

The paper's methodology/ethics section must state: which model pre-labeled the
dataset (Claude, this session), that 100% of pre-labels were human-reviewable and
overridable (not auto-accepted), the override rate (computed by `verify.py`), and
that the second annotator's 250-headline Kappa subset was labeled fully blind to
both the AI pre-labels and the primary annotator's corrections.
