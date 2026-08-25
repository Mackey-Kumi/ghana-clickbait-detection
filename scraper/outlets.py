REQUIRED_KEYS = {"name", "source_style", "mode", "headline_selector", "target_count"}

OUTLETS = [
    {
        "name": "myjoyonline",
        "source_style": "credible",
        "mode": "listing",
        # myjoyonline's /page/N/ URLs serve identical content to page 1 for
        # "news"/"business"/"sports"/"top-story" (confirmed live: page 2+ returns
        # 0 new items) -- those categories are fixed curated blocks, not paginated
        # archives. Aggregating across categories (page 1 only) instead, same
        # approach as "graphic" below.
        "listing_urls": [
            "https://www.myjoyonline.com/category/news/",
            "https://www.myjoyonline.com/category/business/",
            "https://www.myjoyonline.com/category/sports/",
            "https://www.myjoyonline.com/category/top-story/",
            "https://www.myjoyonline.com/category/arts-culture/",
        ],
        "paginate": False,
        "headline_selector": "div.home-section-story-list > a",
        "target_count": 155,
        "max_pages_per_listing": 1,
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
        # "top-stories" is a fixed curated block on citinewsroom too (page 2+
        # returns identical content to page 1, confirmed live). "news" paginates
        # cleanly -- verified 12 pages deep, 15 genuinely new items every page.
        "listing_urls": ["https://citinewsroom.com/category/news/"],
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
