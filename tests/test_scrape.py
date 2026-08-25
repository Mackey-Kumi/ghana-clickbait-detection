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
