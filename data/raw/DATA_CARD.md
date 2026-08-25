# Headline Dataset — Data Card

**Status:** scraping complete — 1,000 headlines collected across 7 outlets.

## Sources

| Outlet | Source style | Base URL |
|---|---|---|
| Myjoyonline | Credible | https://www.myjoyonline.com |
| Graphic Online | Credible | https://www.graphic.com.gh |
| Citinewsroom | Credible | https://citinewsroom.com |
| Ghana News Agency | Credible | https://gna.org.gh |
| GhPage | Clickbait-heavy | https://www.ghpage.com |
| ZionFelix | Clickbait-heavy | https://www.zionfelix.net |
| Yen.com.gh | Clickbait-heavy | https://yen.com.gh |

## Collection method

Myjoyonline, Graphic, Citinewsroom, GNA, GhPage, and ZionFelix: publicly
accessible category/archive listing pages, scraped with `requests` +
BeautifulSoup. Yen.com.gh: its XML sitemap (filtered to entertainment/
celebrity articles) followed by a per-article fetch for the headline, since
its listing pages don't render server-side. No authentication, no
paywalls, no personal data — headline text and article URL only.

## Scrape date

2026-08-25

## Class distribution (by source_style)

| Outlet | Source style | Headlines |
|---|---|---|
| Myjoyonline | Credible | 155 |
| Graphic Online | Credible | 35 |
| Citinewsroom | Credible | 155 |
| Ghana News Agency | Credible | 155 |
| **Credible subtotal** | | **500** |
| GhPage | Clickbait-heavy | 167 |
| ZionFelix | Clickbait-heavy | 167 |
| Yen.com.gh | Clickbait-heavy | 166 |
| **Clickbait-heavy subtotal** | | **500** |
| **Total** | | **1,000** |

All outlets hit their target headline count. No duplicate URLs within any
outlet's file.

## Known limitations

- **Graphic Online is capped at 35** (vs. ~155 for the other credible
  outlets): its category listing pages don't paginate (`?start=N` returns
  identical content), and only 2 of its categories (general-news,
  business-news) share a consistent, scrapable template — other categories
  (politics, education, sports) use inconsistent per-page markup from
  Joomla's page builder. The other 3 credible outlets absorb the volume
  difference, so credible/clickbait-heavy totals stay balanced at 500/500,
  but Graphic is proportionally under-represented within the credible
  bucket.
- **Myjoyonline is an aggregate of 5 categories** (news, business, sports,
  top-story, arts-culture), page 1 only — its category pages don't support
  `/page/N/` pagination (confirmed live: page 2+ returns identical content
  to page 1 for every category tested). This means myjoyonline headlines
  skew toward each category's most recent/most prominent stories rather
  than a deep chronological archive.
- **ghgossip.com and ameyawdebrah.com were deliberately excluded** from the
  clickbait-heavy bucket — both disallow `ClaudeBot` in robots.txt.
  **adomonline.com was excluded** despite being scrapable — it's under the
  same media group (EIB Network) as Myjoyonline and editorially closer to
  credible, so it would have mislabeled the source-diversity signal.
- **Yen.com.gh headlines come from one sitemap shard**
  (`article-sitemap-9.xml`), filtered to `/entertainment/celebrities/`
  URLs, not a category listing page — its listing pages don't render
  server-side. This is a single time-window slice of Yen's celebrity
  coverage rather than a rolling archive crawl.

## Annotation (Stage 2)

**Method:** Claude (this session) pre-labeled all 1,000 headlines against
`docs/ANNOTATION_CODEBOOK.md`, with a one-line rationale per headline citing
the specific signal observed. Every pre-label was then reviewed by the
primary annotator via `annotate/verify.py`, which could accept or override
each one — the pre-label was a draft, not the answer. The codebook itself was
revised three times during verification as the primary annotator identified
gaps in the AI's reasoning (see git history for
`docs/ANNOTATION_CODEBOOK.md`): (1) disturbing subject matter is not itself a
Clickbait signal — the test is whether the headline supplies reportable
substance (who's responsible, what action was taken) alongside the
disturbing content, not whether the topic is upsetting; (2) a quote is not
automatically Informative — the test is whether the framing around it adds a
fact the quote alone doesn't give you, not merely whether the quote is real
and complete; (3) vague hype adjectives ("huge", "plush", "stunning") with no
verifiable detail function as a curiosity gap even in an ordinary declarative
sentence.

**Final label distribution (1,000 headlines, primary annotator's verified
labels — this is the dataset's ground truth):**

| Label | Count | % |
|---|---|---|
| Informative | 794 | 79.4% |
| Clickbait | 196 | 19.6% |
| Ambiguous | 10 | 1.0% |

By source style: credible = 480 Informative / 15 Clickbait / 5 Ambiguous;
clickbait-heavy = 314 Informative / 181 Clickbait / 5 Ambiguous.

**AI pre-label override rate:** the primary annotator overrode 167/1,000
(16.7%) of Claude's pre-labels. Most overrides moved a pre-label from
Informative to Clickbait, concentrated in headlines matching the three
codebook gaps above (quote-led headlines with no anchoring fact, disturbing
first-person quotes with no accountability information, and vague-hype-only
descriptions) — these were pre-labeling blind spots identified and corrected
during verification, not random noise.

**Second annotator / Cohen's Kappa:** a 250-headline stratified random
subset was independently labeled by a second annotator, blind to both the AI
pre-labels and the primary annotator's corrections (`id`-only file, no
url/outlet). Result: **κ = 0.057** (raw agreement 54.6%, 249/250 items
paired — 1 left blank). By the Landis & Koch scale this is "slight
agreement," barely above chance.

This number needs a specific caveat: **the second annotator labeled from the
spreadsheet alone, without reading the codebook or being briefed on its
criteria.** Cohen's Kappa is normally used to validate whether a *shared,
trained* annotation scheme can be applied consistently by different people;
what was measured here is closer to agreement between a codebook-trained
rater and an untrained one working from intuition. The confusion matrix shows
this is systematic, not noisy: the second annotator's Clickbait rate (104/249,
41.8%) was 2.5x the primary annotator's (41/249, 16.5%) on the same items, and
86 of the 205 headlines the primary annotator called Informative were called
Clickbait by the second annotator — a divergence in what "clickbait" means
absent explicit criteria, not disagreement on close calls. This is treated as
a reportable finding about task/scheme necessity (see the paper's Discussion
section) rather than evidence against the primary annotator's labels, which
remain the dataset's ground truth.

**Ambiguous rate:** 10/1,000 (1.0%) — headlines the primary annotator judged
genuinely hard to place under the codebook even after refinement. Excluded
from model training per the original design; retained in the dataset as a
measure of annotation difficulty.
