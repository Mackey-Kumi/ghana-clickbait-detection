# AI-Use Disclosure

I used Claude Code (Anthropic) during this project. This file lists where,
and how I checked its output.

## Where AI was used

| Area | What the AI did | How I verified it |
|---|---|---|
| Annotation | Produced a draft label and one-line reason for each of the 1,000 headlines against my codebook (`data/processed/pre_labels.csv`) | I reviewed every one of the 1,000 drafts myself with `annotate/verify.py` (about five hours) and overrode 167 (16.7%). My labels, not the AI's, are the ground truth. The override table is in the manuscript (Table 2) and `data/processed/verified_labels.csv` records both labels for every headline |
| Codebook | Helped write the first codebook draft | I revised it three times when the drafts kept getting the same kinds of headline wrong (quotes, disturbing topics, vague hype). Every revision came from my own judgement on real headlines |
| Code | Coding assistant for the scraper, annotation tools, notebooks and Kaggle scripts | Unit tests in `tests/` (scraping, annotation, data splitting); every notebook re-run end to end with outputs saved; Kaggle logs saved in `kaggle/experiments/*/output/` |
| Literature | Suggested candidate references | Each reference was checked to exist before being cited; references I could not confirm were not used |
| Writing | Helped draft the manuscript and these repository documents | I reviewed and edited the text. Every number in the manuscript was checked against the saved results files listed in its Appendix A |

## What is my own work

The research question and scope, the choice of outlets, the labelling
decisions on all 1,000 headlines, the three codebook revisions, the decision
to keep the zero-shot comparison and drop the planned web app, and the
interpretation of the results.

## One important finding about the AI's role

The AI pre-labeller under-called clickbait badly: it flagged only 32 of the
196 headlines I labelled Clickbait. A dataset built from its labels alone
would have been about 94% Informative. This is why every draft label was
human-reviewed, and it is discussed in the manuscript.
