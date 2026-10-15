# Ethics Statement

## Data collection

- Only publicly accessible pages were scraped. No logins, paywalls or
  private content.
- Each outlet's `robots.txt` was respected. Two gossip sites
  (ghgossip.com and ameyawdebrah.com) disallow AI crawlers and were
  excluded rather than worked around.
- The scraper identifies itself with a User-Agent string, waits 1.5 seconds
  between requests and retries failed requests at most twice, to keep load on
  the sites minimal.
- Only headline text and article URLs were collected. No article bodies, no
  comments, and no personal data about readers or authors.
- Headlines mention public figures only as they already appear in published
  news.

## Annotation

- The second annotator received only anonymous IDs and headline text
  (`data/processed/second_annotator_subset.xlsx`). They are not named
  anywhere in the repository or the manuscript.
- The ID-to-URL mapping file stayed with the primary annotator. It contains
  no personal data, only public article URLs and outlet names.

## Data access and restrictions

- Everything in this repository is public news headlines and labels derived
  from them. No restricted or licensed datasets, no personal data, and no
  passwords or API keys are committed (the full git history was checked
  before the repository was made public).
- The Kaggle dataset `mackeykumi/dcit316-annotated-headlines` is a private
  copy of `data/processed/annotated_headlines.csv` used only to run training
  on Kaggle's GPUs. It is not needed to reproduce anything: the same file is
  in this repository.
- Anyone re-running the scraper should check the outlets' current
  `robots.txt` and terms first, since they may have changed since August 2026.

## Responsible use of the results

- Labelling a headline "clickbait" is a judgement about writing style. It is
  not a claim that the story is false.
- The per-outlet figures describe this sample only and must not be read as a
  ranking of which outlets are trustworthy.
- The best model flags about two informative headlines for every real piece
  of clickbait it catches (precision 0.468). It is suitable at most for a
  reader-facing warning, never for blocking or censoring content.

## AI assistance

See `docs/AI_USE_DISCLOSURE.md`.
