from annotate.merge_final import build_final_rows


def test_build_final_rows_renames_human_label_to_label():
    verified_rows = [
        {"url": "https://a.com/1/", "outlet": "x", "source_style": "credible", "headline_text": "H1", "ai_label": "Clickbait", "ai_rationale": "R", "human_label": "Informative", "overridden": "True"},
    ]
    result = build_final_rows(verified_rows)
    assert result == [
        {"url": "https://a.com/1/", "outlet": "x", "source_style": "credible", "headline_text": "H1", "label": "Informative"},
    ]
