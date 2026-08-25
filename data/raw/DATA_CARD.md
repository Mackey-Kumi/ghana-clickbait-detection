# Headline Dataset — Data Card

**Status:** scraping not yet run — this section is filled in after `scraper/scrape.py` completes.

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

TODO: fill in after running `python scraper/scrape.py`.

## Class distribution (by source_style)

TODO: fill in after running `python scraper/scrape.py` — read counts from its
summary output.

## Known limitations

TODO: fill in after Stage 2 annotation (e.g. inter-annotator agreement,
ambiguous-headline rate, any outlet that fell short of its target).
