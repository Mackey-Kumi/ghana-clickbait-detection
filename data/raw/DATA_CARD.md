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
- TODO: fill in after Stage 2 annotation (inter-annotator agreement,
  ambiguous-headline rate).
