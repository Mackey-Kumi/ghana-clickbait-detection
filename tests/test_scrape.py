from scraper.scrape import extract_headlines, crawl_outlet


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
