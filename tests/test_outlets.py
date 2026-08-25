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
