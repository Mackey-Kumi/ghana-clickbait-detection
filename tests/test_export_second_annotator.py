from annotate.export_second_annotator import build_subset


def test_build_subset_produces_target_total():
    rows = [
        {"url": f"https://a.com/{i}/", "outlet": "a", "source_style": "credible", "headline_text": f"H{i}"}
        for i in range(50)
    ] + [
        {"url": f"https://b.com/{i}/", "outlet": "b", "source_style": "clickbait_heavy", "headline_text": f"H{i}"}
        for i in range(50)
    ]
    subset_rows, mapping_rows = build_subset(rows, target_total=10, seed=1)
    assert len(subset_rows) == 10
    assert len(mapping_rows) == 10


def test_build_subset_hides_url_and_outlet_from_subset_rows():
    rows = [
        {"url": "https://ghpage.com/1/", "outlet": "ghpage", "source_style": "clickbait_heavy", "headline_text": "H1"},
        {"url": "https://graphic.com.gh/2/", "outlet": "graphic", "source_style": "credible", "headline_text": "H2"},
    ]
    subset_rows, mapping_rows = build_subset(rows, target_total=2, seed=1)
    for row in subset_rows:
        assert set(row.keys()) == {"id", "headline_text", "label"}


def test_build_subset_mapping_allows_merge_back():
    rows = [{"url": "https://a.com/1/", "outlet": "a", "source_style": "credible", "headline_text": "H1"}]
    subset_rows, mapping_rows = build_subset(rows, target_total=1, seed=1)
    assert mapping_rows[0]["id"] == subset_rows[0]["id"]
    assert mapping_rows[0]["url"] == "https://a.com/1/"


def test_build_subset_is_reproducible_with_same_seed():
    rows = [
        {"url": f"https://a.com/{i}/", "outlet": "a", "source_style": "credible", "headline_text": f"H{i}"}
        for i in range(20)
    ]
    subset1, _ = build_subset(rows, target_total=5, seed=7)
    subset2, _ = build_subset(rows, target_total=5, seed=7)
    assert subset1 == subset2
