from annotate.kappa import cohens_kappa, load_paired_labels
from annotate.csv_io import write_csv_rows


def test_cohens_kappa_perfect_agreement():
    labels_a = ["Clickbait", "Informative", "Ambiguous", "Clickbait"]
    labels_b = ["Clickbait", "Informative", "Ambiguous", "Clickbait"]
    assert cohens_kappa(labels_a, labels_b) == 1.0


def test_cohens_kappa_textbook_example():
    # Confusion matrix (A rows, B cols), N=50:
    #        B=Yes  B=No
    # A=Yes    20     5
    # A=No     10    15
    # po=(20+15)/50=0.7, pe=(25/50*30/50)+(25/50*20/50)=0.5, kappa=(0.7-0.5)/0.5=0.4
    labels_a = ["Yes"] * 20 + ["Yes"] * 5 + ["No"] * 10 + ["No"] * 15
    labels_b = ["Yes"] * 20 + ["No"] * 5 + ["Yes"] * 10 + ["No"] * 15
    result = cohens_kappa(labels_a, labels_b)
    assert abs(result - 0.4) < 1e-9


def test_cohens_kappa_returns_one_when_expected_agreement_is_total():
    labels_a = ["Clickbait"] * 5
    labels_b = ["Clickbait"] * 5
    assert cohens_kappa(labels_a, labels_b) == 1.0


def test_load_paired_labels_joins_via_mapping(tmp_path):
    verified_path = str(tmp_path / "verified.csv")
    mapping_path = str(tmp_path / "mapping.csv")
    second_path = str(tmp_path / "second.csv")

    write_csv_rows([{"url": "https://a.com/1/", "human_label": "Clickbait"}], verified_path, ["url", "human_label"])
    write_csv_rows([{"id": "H001", "url": "https://a.com/1/", "outlet": "a", "source_style": "credible"}], mapping_path, ["id", "url", "outlet", "source_style"])
    write_csv_rows([{"id": "H001", "headline_text": "H1", "label": "Informative"}], second_path, ["id", "headline_text", "label"])

    labels_a, labels_b = load_paired_labels(verified_path, mapping_path, second_path)
    assert labels_a == ["Clickbait"]
    assert labels_b == ["Informative"]


def test_load_paired_labels_skips_unfilled_second_annotator_rows(tmp_path):
    verified_path = str(tmp_path / "verified.csv")
    mapping_path = str(tmp_path / "mapping.csv")
    second_path = str(tmp_path / "second.csv")

    write_csv_rows([{"url": "https://a.com/1/", "human_label": "Clickbait"}], verified_path, ["url", "human_label"])
    write_csv_rows([{"id": "H001", "url": "https://a.com/1/", "outlet": "a", "source_style": "credible"}], mapping_path, ["id", "url", "outlet", "source_style"])
    write_csv_rows([{"id": "H001", "headline_text": "H1", "label": ""}], second_path, ["id", "headline_text", "label"])

    labels_a, labels_b = load_paired_labels(verified_path, mapping_path, second_path)
    assert labels_a == []
    assert labels_b == []
