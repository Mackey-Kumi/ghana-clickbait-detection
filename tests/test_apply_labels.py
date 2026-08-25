from annotate.apply_labels import merge_labels, apply_labels
from annotate.csv_io import write_csv_rows, read_csv_rows
from annotate.build_pre_label_template import PRE_LABEL_FIELDS


def test_merge_labels_updates_matching_url_only():
    rows = [
        {"url": "https://example.com/1/", "ai_label": "", "ai_rationale": ""},
        {"url": "https://example.com/2/", "ai_label": "", "ai_rationale": ""},
    ]
    updates = {"https://example.com/1/": ("Clickbait", "Uses false urgency marker 'BREAKING'.")}
    result = merge_labels(rows, updates)
    assert result[0]["ai_label"] == "Clickbait"
    assert result[0]["ai_rationale"] == "Uses false urgency marker 'BREAKING'."
    assert result[1]["ai_label"] == ""


def test_apply_labels_persists_to_file(tmp_path):
    path = str(tmp_path / "pre_labels.csv")
    write_csv_rows(
        [{"url": "https://example.com/1/", "outlet": "x", "source_style": "credible", "headline_text": "H1", "ai_label": "", "ai_rationale": ""}],
        path,
        PRE_LABEL_FIELDS,
    )
    apply_labels(path, {"https://example.com/1/": ("Informative", "States the actual news.")})
    result = read_csv_rows(path)
    assert result[0]["ai_label"] == "Informative"
    assert result[0]["ai_rationale"] == "States the actual news."
