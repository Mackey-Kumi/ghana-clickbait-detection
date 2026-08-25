from annotate.build_pre_label_template import build_template


def test_build_template_produces_empty_label_columns():
    source_rows = [
        {"outlet": "myjoyonline", "source_style": "credible", "headline_text": "A headline", "url": "https://example.com/1/", "scraped_date": "2026-08-25"},
    ]
    result = build_template(source_rows)
    assert result == [
        {
            "url": "https://example.com/1/",
            "outlet": "myjoyonline",
            "source_style": "credible",
            "headline_text": "A headline",
            "ai_label": "",
            "ai_rationale": "",
        }
    ]
