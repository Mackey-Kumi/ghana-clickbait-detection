# Headline Scraper — Design Spec

Date: 2026-08-25
Stage: DCIT 316 project, Stage 1 (Scraping & repo setup)
Source requirements: `end-of-sem-research-writeup.pdf` (project proposal)

## Context

The project proposal specifies scraping headlines from 5 Ghanaian news outlets using
`requests` + BeautifulSoup. Before committing to that outlet list, each candidate was probed
live (raw `curl` fetch, checked for headline text in server-rendered HTML vs. JS-rendered
shells vs. active bot-protection) to confirm feasibility. Findings:

- **GhanaWeb** (originally proposed) returns an active proof-of-work anti-bot challenge
  page, not a rendering issue — bypassing it would mean circumventing a deliberate
  security control, which conflicts with the project's "ethically clean" framing. Dropped.
- **Pulse Ghana** and **PeaceFMOnline** are JS-rendered SPAs (React/Vue hydration data,
  no headline text in raw HTML) — would need Playwright. Not selected for this dataset,
  since enough static-friendly alternatives exist to keep the scraper single-toolchain.
- **Kuulpeeps.com** silently drops non-browser TLS connections (times out, 0 bytes) —
  likely Cloudflare fingerprint-blocking. Dropped rather than chased.
- **Ghanacelebrities.com** returns HTTP 500 (broken site currently). Dropped.
- 14 other outlets were confirmed to serve headline text directly in server-rendered HTML,
  reachable with plain `requests` + BeautifulSoup, no browser automation needed.

## Final Outlet List (8)

| Outlet | Source style | Base domain |
|---|---|---|
| Myjoyonline | Credible | myjoyonline.com |
| Graphic Online | Credible | graphic.com.gh |
| Citinewsroom | Credible | citinewsroom.com |
| Ghana News Agency | Credible | gna.org.gh |
| GhPage | Clickbait-heavy | ghpage.com |
| ZionFelix | Clickbait-heavy | zionfelix.net |
| GhGossip | Clickbait-heavy | ghgossip.com |
| AmeyawDebrah | Clickbait-heavy | ameyawdebrah.com |

All 8 confirmed reachable via plain `requests` + BeautifulSoup (no Playwright dependency
needed for data collection). "Source style" here (stored as `source_style` in the output
CSV) is used to guide outlet selection and target diversity — it is **not** the ground-truth
annotation label. The
actual Clickbait/Informative/Ambiguous label is assigned per-headline during Stage 2
annotation, independent of source.

## Target Dataset Size

**1,000 headlines total, ~125 per outlet.** This is a deliberate increase over the
proposal's original 600–700 target — feasible without added scraping complexity (same
code, just crawl a few more archive pages per outlet), at the cost of more annotation
time in Stage 2. Splitting evenly across 4 credible + 4 clickbait-heavy outlets (vs. the
original plan's 2 outlets per style bucket) also gives more headroom for a held-out-outlet
generalization check later (train on 3 outlets per class, test generalization on the 4th) —
this guards against models learning outlet-specific formatting quirks instead of actual
clickbait language.

## Architecture

```
end-of-sem-research/
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   ├── raw/              # per-outlet CSVs + combined CSV + DATA_CARD.md
│   └── processed/        # empty for now — used in Stage 2 (annotation)
├── scraper/
│   ├── outlets.py        # per-outlet config: archive URL pattern, pagination, CSS selectors
│   ├── scrape.py         # main entrypoint: crawls all outlets, writes CSVs
│   └── utils.py          # request-with-retry, rate limiting, dedupe
├── notebooks/            # empty for now — used in Stage 3+ (modeling/EDA)
├── app/                  # empty for now — used in Stage 5 (Streamlit)
└── docs/superpowers/specs/
```

Per-outlet scraping config (archive URL pattern, headline selector, link selector) lives
entirely in `outlets.py` as data, not scattered through the crawl logic — a new outlet or
a selector fix touches one file, not the crawl loop.

## Data Flow

For each outlet:
1. Fetch archive/category listing pages starting at page 1.
2. Parse headline text + article URL from each page with BeautifulSoup.
3. Dedupe by URL within the outlet.
4. Stop when either: ~125 unique headlines collected, a page returns no new headlines
   (end of archive reached), or a safety cap (~40 pages) is hit.
5. Apply a polite delay (1–2s) between requests.

Each collected row: `{outlet, source_style (credible/clickbait_heavy), url, headline_text, scraped_date}`.

Output: one CSV per outlet in `data/raw/`, plus a combined `data/raw/headlines_combined.csv`.

## Error Handling

- A broken selector on one outlet must not kill the whole run. If an outlet returns zero
  headlines on its first page, log it as failed and move to the next outlet.
- Network errors get 2 retries with backoff before the request is counted as failed.
- A summary at the end of the run reports per-outlet counts and any failures, so selector
  issues are visible immediately rather than discovered later as a silently-short dataset.

## Verification Approach

This is a one-off data collection script, not a long-lived service — formal unit tests
are not warranted. Verification is a `--dry-run` mode: fetch only page 1 per outlet and
print sample extracted headlines + counts, so selector correctness can be checked by eye
per outlet before committing to the full ~125-per-outlet crawl. Archive/category page
markup has only been inspected at the homepage level so far — exact selectors are
determined and validated per outlet during implementation.

## Ethics Artifact

`data/raw/DATA_CARD.md` is created as part of this stage (structure only) and filled in
after scraping completes, documenting: source URLs, scrape date, class distribution
(by source_style), and known limitations. This satisfies the "full data card" deliverable
from the project proposal's ethics section — headline text only, no personal data, no
authentication or paywall bypass involved for any of the 8 selected outlets.
