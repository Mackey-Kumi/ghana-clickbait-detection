import os

from annotate.verify import resolve_decision, load_verified_urls, next_unverified_rows, run, VERIFIED_FIELDS
from annotate.csv_io import write_csv_rows, read_csv_rows
from annotate.build_pre_label_template import PRE_LABEL_FIELDS


def test_resolve_decision_accepts_ai_label_on_empty_input():
    label, overridden = resolve_decision("", "Clickbait")
    assert label == "Clickbait"
    assert overridden is False


def test_resolve_decision_overrides_with_different_key():
    label, overridden = resolve_decision("i", "Clickbait")
    assert label == "Informative"
    assert overridden is True


def test_resolve_decision_same_key_as_ai_label_not_counted_as_override():
    label, overridden = resolve_decision("c", "Clickbait")
    assert label == "Clickbait"
    assert overridden is False


def test_resolve_decision_unrecognized_key_returns_none():
    label, overridden = resolve_decision("x", "Clickbait")
    assert label is None
    assert overridden is None


def test_load_verified_urls_empty_when_file_missing(tmp_path):
    result = load_verified_urls(str(tmp_path / "does_not_exist.csv"))
    assert result == set()


def test_next_unverified_rows_skips_already_verified():
    pre_label_rows = [{"url": "https://a.com/1/"}, {"url": "https://a.com/2/"}]
    verified_urls = {"https://a.com/1/"}
    result = next_unverified_rows(pre_label_rows, verified_urls)
    assert result == [{"url": "https://a.com/2/"}]


def test_run_writes_verified_labels_and_tracks_overrides(tmp_path):
    pre_labels_path = str(tmp_path / "pre_labels.csv")
    verified_path = str(tmp_path / "verified_labels.csv")
    write_csv_rows(
        [
            {"url": "https://a.com/1/", "outlet": "x", "source_style": "credible", "headline_text": "H1", "ai_label": "Clickbait", "ai_rationale": "R1"},
            {"url": "https://a.com/2/", "outlet": "x", "source_style": "credible", "headline_text": "H2", "ai_label": "Informative", "ai_rationale": "R2"},
        ],
        pre_labels_path,
        PRE_LABEL_FIELDS,
    )
    inputs = iter(["", "c"])
    run(
        pre_labels_path=pre_labels_path,
        verified_path=verified_path,
        input_fn=lambda prompt: next(inputs),
        print_fn=lambda msg: None,
    )
    result = read_csv_rows(verified_path)
    assert result[0]["human_label"] == "Clickbait"
    assert result[0]["overridden"] == "False"
    assert result[1]["human_label"] == "Clickbait"
    assert result[1]["overridden"] == "True"


def test_run_is_resumable_skipping_already_verified(tmp_path):
    pre_labels_path = str(tmp_path / "pre_labels.csv")
    verified_path = str(tmp_path / "verified_labels.csv")
    write_csv_rows(
        [
            {"url": "https://a.com/1/", "outlet": "x", "source_style": "credible", "headline_text": "H1", "ai_label": "Clickbait", "ai_rationale": "R1"},
            {"url": "https://a.com/2/", "outlet": "x", "source_style": "credible", "headline_text": "H2", "ai_label": "Informative", "ai_rationale": "R2"},
        ],
        pre_labels_path,
        PRE_LABEL_FIELDS,
    )
    write_csv_rows(
        [
            {"url": "https://a.com/1/", "outlet": "x", "source_style": "credible", "headline_text": "H1", "ai_label": "Clickbait", "ai_rationale": "R1", "human_label": "Clickbait", "overridden": False},
        ],
        verified_path,
        VERIFIED_FIELDS,
    )
    inputs = iter([""])
    run(
        pre_labels_path=pre_labels_path,
        verified_path=verified_path,
        input_fn=lambda prompt: next(inputs),
        print_fn=lambda msg: None,
    )
    result = read_csv_rows(verified_path)
    assert len(result) == 2
    assert result[1]["url"] == "https://a.com/2/"


def test_run_stops_early_on_q(tmp_path):
    pre_labels_path = str(tmp_path / "pre_labels.csv")
    verified_path = str(tmp_path / "verified_labels.csv")
    write_csv_rows(
        [
            {"url": "https://a.com/1/", "outlet": "x", "source_style": "credible", "headline_text": "H1", "ai_label": "Clickbait", "ai_rationale": "R1"},
        ],
        pre_labels_path,
        PRE_LABEL_FIELDS,
    )
    inputs = iter(["q"])
    run(
        pre_labels_path=pre_labels_path,
        verified_path=verified_path,
        input_fn=lambda prompt: next(inputs),
        print_fn=lambda msg: None,
    )
    assert not os.path.exists(verified_path)
