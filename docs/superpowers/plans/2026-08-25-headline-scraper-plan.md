# Headline Scraper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a scraper that collects 1,000 Ghanaian news headlines (500 credible / 500 clickbait-heavy) from 7 outlets into CSVs for Stage 2 annotation.

**Architecture:** A config-driven crawler with two extraction modes. `scraper/outlets.py` holds per-outlet data (URLs, CSS selectors, targets, mode) — no per-outlet code branches anywhere else. `scraper/scrape.py` has four pure, independently-testable functions: `extract_headlines` + `crawl_outlet` for outlets with a category/archive listing page (`mode: "listing"`), and `extract_sitemap_urls` + `crawl_sitemap_outlet` for outlets scraped via their XML sitemap plus a per-article headline fetch (`mode: "sitemap"`) — used for Yen.com.gh, whose category listing pages don't render server-side but whose sitemap + article pages do. A thin `run()`/CLI wrapper dispatches on `mode` and wires everything to real HTTP calls. `scraper/utils.py` holds the two cross-cutting concerns: retrying HTTP fetches and deduping rows.

**Tech Stack:** Python 3, `requests`, `beautifulsoup4`, `pytest` (stdlib `csv`/`argparse`/`re` for the rest — no `pandas` needed yet).

## Global Constraints

- User-Agent for all requests: `"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"` — verified during outlet research to work against all 7 selected outlets.
- Delay of 1.5s between HTTP requests (politeness), defined once as `REQUEST_DELAY_SECONDS` in `scraper/utils.py`. This applies per-request in `mode: "sitemap"` too (one request per article), not just per-page.
- Network retry: 2 retries with a 2s backoff before a fetch is treated as failed.
- Final dataset CSV columns, in this exact order: `outlet, source_style, headline_text, url, scraped_date`.
- `source_style` values are exactly `"credible"` or `"clickbait_heavy"` — this is a source-diversity label, never the ground-truth annotation label (that comes in Stage 2, per-headline).
- Target: 1,000 total headlines across 7 outlets: myjoyonline (155), graphic (35), citinewsroom (155), gna (155), ghpage (167), zionfelix (167), yen (166). Sums to 1,000.
- No Playwright / browser automation — all 7 outlets confirmed reachable via plain `requests` + BeautifulSoup.
- ghgossip.com and ameyawdebrah.com are excluded — both disallow `ClaudeBot` in robots.txt, a deliberate opt-out from Anthropic's crawler that a differently-branded User-Agent must not be used to route around. Do not add them back without revisiting this.
- adomonline.com is excluded from the clickbait-heavy bucket — it's under the same media group (EIB Network) as Myjoyonline and editorially closer to credible, so including it there would mislabel the source-diversity signal.

---

### Task 1: Project scaffold

**Files:**
- Create: `requirements.txt`
- Create: `README.md`
- Create: `data/raw/.gitkeep`, `data/processed/.gitkeep`, `notebooks/.gitkeep`, `app/.gitkeep` (empty-dir placeholders — git doesn't track empty dirs)
- Create: `data/raw/DATA_CARD.md`
- Create: `scraper/__init__.py` (empty)

**Interfaces:**
- Consumes: nothing (first task)
- Produces: the directory layout and installable environment every later task assumes exists

- [ ] **Step 1: Create `requirements.txt`**

```
requests==2.32.3
beautifulsoup4==4.12.3
pytest==8.3.3
```

- [ ] **Step 2: Create the directory placeholders**

```bash
mkdir -p data/raw data/processed notebooks app scraper
touch data/raw/.gitkeep data/processed/.gitkeep notebooks/.gitkeep app/.gitkeep
touch scraper/__init__.py
```

- [ ] **Step 3: Create `data/raw/DATA_CARD.md`**

```markdown
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
```

- [ ] **Step 4: Create `README.md`**

```markdown
# Detecting Clickbait and Sensationalism in Ghanaian Online News Headlines

DCIT 316 — Computational Models for Social Media Mining, University of Ghana, 2025/2026.

## Setup

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Stage 1 — Scraping

\`\`\`bash
python scraper/scrape.py --dry-run   # fetch ~10 headlines/outlet, sanity-check selectors
python scraper/scrape.py             # full collection run, ~1,000 headlines
\`\`\`

Output: `data/raw/<outlet>.csv` per outlet, plus `data/raw/headlines_combined.csv`.

## Project layout

- `scraper/` — headline collection (Stage 1)
- `data/raw/` — scraped, unlabeled headlines + data card
- `data/processed/` — annotated data (Stage 2)
- `notebooks/` — modeling and EDA (Stage 3+)
- `app/` — Streamlit demo (Stage 5)
```

- [ ] **Step 5: Verify the environment installs cleanly**

Run: `pip install -r requirements.txt`
Expected: completes with no errors.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt README.md data/raw/DATA_CARD.md data/raw/.gitkeep data/processed/.gitkeep notebooks/.gitkeep app/.gitkeep scraper/__init__.py
git commit -m "Scaffold project structure for headline scraper"
```

---

### Task 2: `scraper/utils.py` — HTTP retry and dedupe helpers

**Files:**
- Create: `scraper/utils.py`
- Test: `tests/test_utils.py`

**Interfaces:**
- Consumes: nothing beyond `requests` (external lib)
- Produces:
  - `USER_AGENT: str`
  - `REQUEST_DELAY_SECONDS: float`
  - `fetch_with_retry(session, url, retries=2, timeout=15, backoff_seconds=2) -> str | None`
  - `dedupe_rows(rows: list[dict]) -> list[dict]` — dedupes by `row["url"]`, keeps first occurrence, preserves order

- [ ] **Step 1: Write the failing tests**

Create `tests/__init__.py` (empty) and `tests/test_utils.py`:

```python
from unittest.mock import Mock
import requests
from scraper.utils import fetch_with_retry, dedupe_rows


def test_fetch_with_retry_returns_text_on_success():
    session = Mock()
    session.get.return_value = Mock(status_code=200, text="<html>ok</html>")
    result = fetch_with_retry(session, "https://example.com", retries=2, timeout=5, backoff_seconds=0)
    assert result == "<html>ok</html>"
    assert session.get.call_count == 1


def test_fetch_with_retry_retries_then_succeeds():
    session = Mock()
    fail_response = Mock(status_code=500, text="")
    ok_response = Mock(status_code=200, text="<html>ok</html>")
    session.get.side_effect = [fail_response, ok_response]
    result = fetch_with_retry(session, "https://example.com", retries=2, timeout=5, backoff_seconds=0)
    assert result == "<html>ok</html>"
    assert session.get.call_count == 2


def test_fetch_with_retry_returns_none_after_exhausting_retries():
    session = Mock()
    session.get.side_effect = requests.exceptions.Timeout()
    result = fetch_with_retry(session, "https://example.com", retries=2, timeout=5, backoff_seconds=0)
    assert result is None
    assert session.get.call_count == 3


def test_dedupe_rows_removes_duplicate_urls_keeping_first():
    rows = [
        {"url": "https://a.com/1", "headline_text": "First"},
        {"url": "https://a.com/2", "headline_text": "Second"},
        {"url": "https://a.com/1", "headline_text": "First duplicate"},
    ]
    result = dedupe_rows(rows)
    assert len(result) == 2
    assert result[0]["headline_text"] == "First"
    assert result[1]["headline_text"] == "Second"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_utils.py -v`
Expected: FAIL / ERROR — `scraper.utils` does not exist yet.

- [ ] **Step 3: Implement `scraper/utils.py`**

```python
import time

import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
REQUEST_DELAY_SECONDS = 1.5


def fetch_with_retry(session, url, retries=2, timeout=15, backoff_seconds=2):
    for attempt in range(retries + 1):
        try:
            response = session.get(url, timeout=timeout)
            if response.status_code == 200:
                return response.text
        except requests.RequestException:
            pass
        if attempt < retries:
            time.sleep(backoff_seconds)
    return None


def dedupe_rows(rows):
    seen = set()
    result = []
    for row in rows:
        if row["url"] in seen:
            continue
        seen.add(row["url"])
        result.append(row)
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_utils.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add scraper/utils.py tests/__init__.py tests/test_utils.py
git commit -m "Add HTTP retry and dedupe utilities"
```

---

### Task 3: `scraper/outlets.py` — outlet configuration data

**Files:**
- Create: `scraper/outlets.py`
- Test: `tests/test_outlets.py`

**Interfaces:**
- Consumes: nothing
- Produces:
  - `OUTLETS: list[dict]` — every dict has `name, source_style, mode, headline_selector, target_count`. `mode: "listing"` dicts additionally have `listing_urls, paginate, max_pages_per_listing`. `mode: "sitemap"` dicts additionally have `sitemap_url, url_filter`.
  - `REQUIRED_KEYS: set[str]`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_outlets.py`:

```python
from scraper.outlets import OUTLETS, REQUIRED_KEYS


def test_all_outlets_have_required_keys():
    for outlet in OUTLETS:
        assert REQUIRED_KEYS.issubset(outlet.keys())


def test_outlet_names_are_unique():
    names = [o["name"] for o in OUTLETS]
    assert len(names) == len(set(names))


def test_target_counts_sum_to_1000():
    assert sum(o["target_count"] for o in OUTLETS) == 1000


def test_source_styles_are_valid():
    valid = {"credible", "clickbait_heavy"}
    for outlet in OUTLETS:
        assert outlet["source_style"] in valid


def test_listing_mode_outlets_have_listing_fields():
    for outlet in OUTLETS:
        if outlet["mode"] == "listing":
            assert "listing_urls" in outlet
            assert "paginate" in outlet
            assert "max_pages_per_listing" in outlet


def test_sitemap_mode_outlets_have_sitemap_fields():
    for outlet in OUTLETS:
        if outlet["mode"] == "sitemap":
            assert "sitemap_url" in outlet
            assert "url_filter" in outlet
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_outlets.py -v`
Expected: FAIL / ERROR — `scraper.outlets` does not exist yet.

- [ ] **Step 3: Implement `scraper/outlets.py`**

```python
REQUIRED_KEYS = {"name", "source_style", "mode", "headline_selector", "target_count"}

OUTLETS = [
    {
        "name": "myjoyonline",
        "source_style": "credible",
        "mode": "listing",
        "listing_urls": ["https://www.myjoyonline.com/category/news/"],
        "paginate": True,
        "headline_selector": "div.home-section-story-list > a",
        "target_count": 155,
        "max_pages_per_listing": 40,
    },
    {
        "name": "graphic",
        "source_style": "credible",
        "mode": "listing",
        "listing_urls": [
            "https://www.graphic.com.gh/news/general-news.html",
            "https://www.graphic.com.gh/business/business-news.html",
        ],
        "paginate": False,
        "headline_selector": "div.article-header h2 a",
        "target_count": 35,
        "max_pages_per_listing": 1,
    },
    {
        "name": "citinewsroom",
        "source_style": "credible",
        "mode": "listing",
        "listing_urls": ["https://citinewsroom.com/category/top-stories/"],
        "paginate": True,
        "headline_selector": "h3.jeg_post_title > a",
        "target_count": 155,
        "max_pages_per_listing": 40,
    },
    {
        "name": "gna",
        "source_style": "credible",
        "mode": "listing",
        "listing_urls": ["https://gna.org.gh/headline/"],
        "paginate": True,
        "headline_selector": "h2.entry-title > a",
        "target_count": 155,
        "max_pages_per_listing": 40,
    },
    {
        "name": "ghpage",
        "source_style": "clickbait_heavy",
        "mode": "listing",
        "listing_urls": ["https://www.ghpage.com/category/news/"],
        "paginate": True,
        "headline_selector": "h3.entry-title.td-module-title > a",
        "target_count": 167,
        "max_pages_per_listing": 40,
    },
    {
        "name": "zionfelix",
        "source_style": "clickbait_heavy",
        "mode": "listing",
        "listing_urls": ["https://www.zionfelix.net/category/entertainment/"],
        "paginate": True,
        "headline_selector": "h3.entry-title.td-module-title > a",
        "target_count": 167,
        "max_pages_per_listing": 40,
    },
    {
        "name": "yen",
        "source_style": "clickbait_heavy",
        "mode": "sitemap",
        "sitemap_url": "https://yen.com.gh/yen/sitemap/article-sitemap-9.xml",
        "url_filter": "/entertainment/celebrities/",
        "headline_selector": "h1.c-main-headline",
        "target_count": 166,
    },
]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_outlets.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add scraper/outlets.py tests/test_outlets.py
git commit -m "Add outlet configuration for 7 confirmed sources"
```

---

### Task 4: `scraper/scrape.py` — `extract_headlines` (listing-page mode)

**Files:**
- Create: `scraper/scrape.py`
- Test: `tests/test_scrape.py`

**Interfaces:**
- Consumes: nothing beyond `bs4` (external lib)
- Produces: `extract_headlines(html: str, headline_selector: str) -> list[dict]` — each dict has keys `headline_text, url`; entries with no `href` or empty text are skipped

- [ ] **Step 1: Write the failing tests**

Create `tests/test_scrape.py`:

```python
from scraper.scrape import extract_headlines


def test_extract_headlines_wp_style():
    html = """
    <div class="jeg_postblock_content">
      <h3 class="jeg_post_title"><a href="https://example.com/story-1/">First real headline</a></h3>
    </div>
    <div class="jeg_postblock_content">
      <h3 class="jeg_post_title"><a href="https://example.com/story-2/">Second real headline</a></h3>
    </div>
    """
    rows = extract_headlines(html, "h3.jeg_post_title > a")
    assert rows == [
        {"headline_text": "First real headline", "url": "https://example.com/story-1/"},
        {"headline_text": "Second real headline", "url": "https://example.com/story-2/"},
    ]


def test_extract_headlines_skips_empty_text():
    html = '<h3 class="jeg_post_title"><a href="https://example.com/empty/"></a></h3>'
    rows = extract_headlines(html, "h3.jeg_post_title > a")
    assert rows == []


def test_extract_headlines_skips_missing_href():
    html = '<h3 class="jeg_post_title"><a>No link headline</a></h3>'
    rows = extract_headlines(html, "h3.jeg_post_title > a")
    assert rows == []


def test_extract_headlines_graphic_style():
    html = """
    <div class="article-header"><h2><a href="/news/general-news/story-a.html">Headline A text</a></h2></div>
    <div class="article-header"><h2><a href="/news/general-news/story-b.html">Headline B text</a></h2></div>
    """
    rows = extract_headlines(html, "div.article-header h2 a")
    assert rows == [
        {"headline_text": "Headline A text", "url": "/news/general-news/story-a.html"},
        {"headline_text": "Headline B text", "url": "/news/general-news/story-b.html"},
    ]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_scrape.py -v`
Expected: FAIL / ERROR — `scraper.scrape` does not exist yet.

- [ ] **Step 3: Implement `extract_headlines` in `scraper/scrape.py`**

```python
from bs4 import BeautifulSoup


def extract_headlines(html, headline_selector):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for anchor in soup.select(headline_selector):
        href = anchor.get("href")
        text = anchor.get_text(strip=True)
        if not href or not text:
            continue
        rows.append({"headline_text": text, "url": href})
    return rows
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_scrape.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add scraper/scrape.py tests/test_scrape.py
git commit -m "Add headline extraction from listing page HTML"
```

---

### Task 5: `scraper/scrape.py` — `crawl_outlet` (listing-page mode)

**Files:**
- Modify: `scraper/scrape.py`
- Modify: `tests/test_scrape.py`

**Interfaces:**
- Consumes: `extract_headlines(html, headline_selector) -> list[dict]` (Task 4). Outlet config dict shape from `scraper/outlets.py` (Task 3): `listing_urls, paginate, headline_selector, target_count, max_pages_per_listing`.
- Produces: `crawl_outlet(config: dict, fetch_fn: Callable[[str], str | None]) -> list[dict]` — rows deduped by url, capped at `config["target_count"]`. `fetch_fn` is injected so tests never hit the network.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_scrape.py`:

```python
from scraper.scrape import crawl_outlet


def test_crawl_outlet_stops_when_target_reached():
    config = {
        "listing_urls": ["https://example.com/category/news/"],
        "paginate": True,
        "headline_selector": "a.headline",
        "target_count": 2,
        "max_pages_per_listing": 10,
    }
    page_html = (
        '<a class="headline" href="https://example.com/1/">One</a>'
        '<a class="headline" href="https://example.com/2/">Two</a>'
        '<a class="headline" href="https://example.com/3/">Three</a>'
    )
    calls = []

    def fake_fetch(url):
        calls.append(url)
        return page_html

    rows = crawl_outlet(config, fake_fetch)
    assert len(rows) == 2
    assert calls == ["https://example.com/category/news/"]


def test_crawl_outlet_stops_at_end_of_archive():
    config = {
        "listing_urls": ["https://example.com/category/news/"],
        "paginate": True,
        "headline_selector": "a.headline",
        "target_count": 100,
        "max_pages_per_listing": 10,
    }
    page1_html = '<a class="headline" href="https://example.com/1/">One</a>'

    def fake_fetch(url):
        if url.endswith("page/2/"):
            return ""
        return page1_html

    rows = crawl_outlet(config, fake_fetch)
    assert len(rows) == 1


def test_crawl_outlet_aggregates_non_paginating_listings():
    config = {
        "listing_urls": [
            "https://example.com/news/general-news.html",
            "https://example.com/news/business.html",
        ],
        "paginate": False,
        "headline_selector": "a.headline",
        "target_count": 100,
        "max_pages_per_listing": 1,
    }
    pages = {
        "https://example.com/news/general-news.html": '<a class="headline" href="https://example.com/g1/">G1</a>',
        "https://example.com/news/business.html": '<a class="headline" href="https://example.com/b1/">B1</a>',
    }

    def fake_fetch(url):
        return pages[url]

    rows = crawl_outlet(config, fake_fetch)
    assert {r["url"] for r in rows} == {"https://example.com/g1/", "https://example.com/b1/"}


def test_crawl_outlet_stops_on_fetch_failure():
    config = {
        "listing_urls": ["https://example.com/category/news/"],
        "paginate": True,
        "headline_selector": "a.headline",
        "target_count": 100,
        "max_pages_per_listing": 10,
    }

    def fake_fetch(url):
        return None

    rows = crawl_outlet(config, fake_fetch)
    assert rows == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_scrape.py -v`
Expected: the 5 new tests FAIL — `crawl_outlet` does not exist yet.

- [ ] **Step 3: Implement `crawl_outlet` in `scraper/scrape.py`**

Add to `scraper/scrape.py` (keep `extract_headlines` above it):

```python
from urllib.parse import urljoin


def crawl_outlet(config, fetch_fn):
    collected = {}
    for listing_url in config["listing_urls"]:
        page = 1
        while len(collected) < config["target_count"] and page <= config["max_pages_per_listing"]:
            url = listing_url if page == 1 else urljoin(listing_url, f"page/{page}/")
            html = fetch_fn(url)
            if html is None:
                break
            new_rows = extract_headlines(html, config["headline_selector"])
            added = 0
            for row in new_rows:
                if row["url"] not in collected:
                    collected[row["url"]] = row
                    added += 1
            if added == 0:
                break
            if not config["paginate"]:
                break
            page += 1
        if len(collected) >= config["target_count"]:
            break
    return list(collected.values())[: config["target_count"]]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_scrape.py -v`
Expected: 9 passed (4 from Task 4 + 5 new)

- [ ] **Step 5: Commit**

```bash
git add scraper/scrape.py tests/test_scrape.py
git commit -m "Add pagination and stopping logic for outlet crawling"
```

---

### Task 6: `scraper/scrape.py` — sitemap mode (for Yen.com.gh)

**Files:**
- Modify: `scraper/scrape.py`
- Modify: `tests/test_scrape.py`

**Interfaces:**
- Consumes: nothing beyond `bs4`/`re` (external lib + stdlib). Outlet config dict shape from `scraper/outlets.py` (Task 3): `sitemap_url, url_filter, headline_selector, target_count`.
- Produces:
  - `extract_sitemap_urls(sitemap_xml: str, url_filter: str) -> list[str]` — all `<loc>` values containing `url_filter` as a substring, in document order
  - `extract_single_headline(html: str, headline_selector: str) -> str | None`
  - `crawl_sitemap_outlet(config: dict, fetch_fn: Callable[[str], str | None]) -> list[dict]` — fetches the sitemap, filters URLs, then fetches each candidate article page (in order) until `target_count` headlines are collected; pages with no matching headline are skipped, not counted

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_scrape.py`:

```python
from scraper.scrape import extract_sitemap_urls, extract_single_headline, crawl_sitemap_outlet


def test_extract_sitemap_urls_filters_by_substring():
    xml = """
    <urlset>
    <url><loc>https://example.com/politics/1-story/</loc></url>
    <url><loc>https://example.com/entertainment/celebrities/2-story/</loc></url>
    <url><loc>https://example.com/entertainment/celebrities/3-story/</loc></url>
    </urlset>
    """
    urls = extract_sitemap_urls(xml, "entertainment/celebrities")
    assert urls == [
        "https://example.com/entertainment/celebrities/2-story/",
        "https://example.com/entertainment/celebrities/3-story/",
    ]


def test_extract_single_headline_returns_text():
    html = '<h1 class="c-main-headline">A real headline here</h1>'
    assert extract_single_headline(html, "h1.c-main-headline") == "A real headline here"


def test_extract_single_headline_returns_none_when_missing():
    html = "<h1>No matching class</h1>"
    assert extract_single_headline(html, "h1.c-main-headline") is None


def test_crawl_sitemap_outlet_fetches_urls_up_to_target():
    config = {
        "sitemap_url": "https://example.com/sitemap.xml",
        "url_filter": "entertainment",
        "headline_selector": "h1.c-main-headline",
        "target_count": 2,
    }
    sitemap_xml = """
    <urlset>
    <url><loc>https://example.com/entertainment/1/</loc></url>
    <url><loc>https://example.com/entertainment/2/</loc></url>
    <url><loc>https://example.com/entertainment/3/</loc></url>
    </urlset>
    """
    pages = {
        "https://example.com/sitemap.xml": sitemap_xml,
        "https://example.com/entertainment/1/": '<h1 class="c-main-headline">Headline One</h1>',
        "https://example.com/entertainment/2/": '<h1 class="c-main-headline">Headline Two</h1>',
        "https://example.com/entertainment/3/": '<h1 class="c-main-headline">Headline Three</h1>',
    }
    calls = []

    def fake_fetch(url):
        calls.append(url)
        return pages[url]

    rows = crawl_sitemap_outlet(config, fake_fetch)
    assert rows == [
        {"headline_text": "Headline One", "url": "https://example.com/entertainment/1/"},
        {"headline_text": "Headline Two", "url": "https://example.com/entertainment/2/"},
    ]
    assert calls == [
        "https://example.com/sitemap.xml",
        "https://example.com/entertainment/1/",
        "https://example.com/entertainment/2/",
    ]


def test_crawl_sitemap_outlet_skips_pages_with_no_headline():
    config = {
        "sitemap_url": "https://example.com/sitemap.xml",
        "url_filter": "entertainment",
        "headline_selector": "h1.c-main-headline",
        "target_count": 5,
    }
    sitemap_xml = """
    <urlset>
    <url><loc>https://example.com/entertainment/1/</loc></url>
    <url><loc>https://example.com/entertainment/2/</loc></url>
    </urlset>
    """
    pages = {
        "https://example.com/sitemap.xml": sitemap_xml,
        "https://example.com/entertainment/1/": "<h1>no matching class</h1>",
        "https://example.com/entertainment/2/": '<h1 class="c-main-headline">Headline Two</h1>',
    }

    def fake_fetch(url):
        return pages[url]

    rows = crawl_sitemap_outlet(config, fake_fetch)
    assert rows == [{"headline_text": "Headline Two", "url": "https://example.com/entertainment/2/"}]


def test_crawl_sitemap_outlet_returns_empty_when_sitemap_fetch_fails():
    config = {
        "sitemap_url": "https://example.com/sitemap.xml",
        "url_filter": "entertainment",
        "headline_selector": "h1.c-main-headline",
        "target_count": 5,
    }

    def fake_fetch(url):
        return None

    rows = crawl_sitemap_outlet(config, fake_fetch)
    assert rows == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_scrape.py -v`
Expected: the 6 new tests FAIL — the sitemap functions don't exist yet.

- [ ] **Step 3: Implement the sitemap functions in `scraper/scrape.py`**

Add near the top of `scraper/scrape.py` (with the other imports) and anywhere below `crawl_outlet`:

```python
import re


def extract_sitemap_urls(sitemap_xml, url_filter):
    urls = re.findall(r"<loc>(.*?)</loc>", sitemap_xml)
    return [u for u in urls if url_filter in u]


def extract_single_headline(html, headline_selector):
    soup = BeautifulSoup(html, "html.parser")
    node = soup.select_one(headline_selector)
    if node is None:
        return None
    text = node.get_text(strip=True)
    return text or None


def crawl_sitemap_outlet(config, fetch_fn):
    sitemap_xml = fetch_fn(config["sitemap_url"])
    if sitemap_xml is None:
        return []
    candidate_urls = extract_sitemap_urls(sitemap_xml, config["url_filter"])
    rows = []
    for url in candidate_urls:
        if len(rows) >= config["target_count"]:
            break
        html = fetch_fn(url)
        if html is None:
            continue
        text = extract_single_headline(html, config["headline_selector"])
        if text:
            rows.append({"headline_text": text, "url": url})
    return rows
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_scrape.py -v`
Expected: 15 passed (9 from Tasks 4-5 + 6 new)

- [ ] **Step 5: Commit**

```bash
git add scraper/scrape.py tests/test_scrape.py
git commit -m "Add sitemap-driven crawling mode for Yen.com.gh"
```

---

### Task 7: `scraper/scrape.py` — CLI, CSV output, and live dry run

**Files:**
- Modify: `scraper/scrape.py`
- Modify: `data/raw/DATA_CARD.md` (fill in after the live dry run)

**Interfaces:**
- Consumes: `crawl_outlet` (Task 5), `crawl_sitemap_outlet` (Task 6), `OUTLETS` (Task 3), `fetch_with_retry`, `dedupe_rows`, `USER_AGENT`, `REQUEST_DELAY_SECONDS` (Task 2)
- Produces: `write_csv(rows, path)`, `run(dry_run=False)`, `main()` CLI entrypoint; `data/raw/<outlet>.csv` and `data/raw/headlines_combined.csv` on disk after a real run

This task has no new unit-testable pure logic (it's I/O wiring), so verification is a real dry run against the live outlets instead of mocked tests — this is the "does the crawler actually work against the real sites" check.

- [ ] **Step 1: Implement CSV writing, `run()`, and CLI in `scraper/scrape.py`**

Add to `scraper/scrape.py`:

```python
import argparse
import csv
import os
import time
from datetime import date

import requests

from scraper.outlets import OUTLETS
from scraper.utils import USER_AGENT, REQUEST_DELAY_SECONDS, fetch_with_retry, dedupe_rows

CSV_FIELDS = ["outlet", "source_style", "headline_text", "url", "scraped_date"]


def write_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def run(dry_run=False):
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    def fetch(url):
        html = fetch_with_retry(session, url)
        time.sleep(REQUEST_DELAY_SECONDS)
        return html

    today = date.today().isoformat()
    all_rows = []
    summary = []

    for outlet in OUTLETS:
        config = dict(outlet)
        if dry_run:
            config["target_count"] = 10
            if config["mode"] == "listing":
                config["max_pages_per_listing"] = 1

        if config["mode"] == "sitemap":
            rows = crawl_sitemap_outlet(config, fetch)
        else:
            rows = crawl_outlet(config, fetch)

        for row in rows:
            row["outlet"] = outlet["name"]
            row["source_style"] = outlet["source_style"]
            row["scraped_date"] = today

        rows = dedupe_rows(rows)
        write_csv(rows, f"data/raw/{outlet['name']}.csv")
        all_rows.extend(rows)
        summary.append((outlet["name"], len(rows), config["target_count"]))

    write_csv(all_rows, "data/raw/headlines_combined.csv")

    print(f"{'Outlet':<15}{'Collected':<12}{'Target':<10}")
    for name, collected, target in summary:
        flag = "" if collected >= target else "  <-- short of target"
        print(f"{name:<15}{collected:<12}{target:<10}{flag}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Fetch ~10 headlines/outlet only, for selector sanity-checking")
    args = parser.parse_args()
    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the full test suite to confirm nothing broke**

Run: `pytest tests/ -v`
Expected: all tests from Tasks 2-6 still pass (this task added no new pure-logic tests).

- [ ] **Step 3: Run a live dry run against the real outlets**

Run: `python scraper/scrape.py --dry-run`

Expected: a summary table printing all 7 outlets with `Collected` close to 10 each (some may fall short if a listing page genuinely has fewer than 10 items, which is fine — Yen's sitemap shard has thousands of candidates so it should always hit 10). Then inspect the output:

```bash
head -5 data/raw/myjoyonline.csv
head -5 data/raw/graphic.csv
head -5 data/raw/ghpage.csv
head -5 data/raw/yen.csv
```

Confirm `headline_text` values are real, readable headlines (not nav labels, not empty, not HTML fragments) and `url` values are real article URLs. If any outlet's selector has drifted since this plan was written, fix the `headline_selector` (or for Yen, `url_filter`/`sitemap_url`) for that outlet in `scraper/outlets.py` (Task 3's file) and re-run the dry run before proceeding — do not move on with a silently broken outlet.

- [ ] **Step 4: Run the full collection**

Run: `python scraper/scrape.py`

Expected: takes a while — Yen alone makes ~166+ individual article requests at 1.5s each (~4-5 minutes just for Yen), plus the other 6 outlets' listing-page crawls. Final summary should show all 7 outlets at or near their targets, totaling ~1,000 in `data/raw/headlines_combined.csv`.

- [ ] **Step 5: Fill in `data/raw/DATA_CARD.md`**

Replace the three `TODO` sections with the actual scrape date and the per-outlet/per-source_style counts from the summary table Step 4 printed.

- [ ] **Step 6: Commit**

```bash
git add scraper/scrape.py data/raw/DATA_CARD.md
git commit -m "Add CLI, CSV output, and run full headline collection"
```

Note: the scraped CSVs in `data/raw/` are a data artifact, not source code — commit them too if the project wants the dataset versioned in git (recommended, given the proposal's "reproducible GitHub repo" deliverable and the dataset's small size, well under GitHub's file-size limits):

```bash
git add data/raw/*.csv
git commit -m "Add scraped headline dataset (~1,000 headlines, 7 outlets)"
```
