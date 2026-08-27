import pandas as pd

from models.data import load_labeled_dataset, make_train_test_split, held_out_outlet_split


def test_load_labeled_dataset_excludes_ambiguous(tmp_path):
    path = tmp_path / "labeled.csv"
    pd.DataFrame(
        [
            {"url": "https://a.com/1/", "outlet": "a", "source_style": "credible", "headline_text": "H1", "label": "Informative"},
            {"url": "https://a.com/2/", "outlet": "a", "source_style": "credible", "headline_text": "H2", "label": "Clickbait"},
            {"url": "https://a.com/3/", "outlet": "a", "source_style": "credible", "headline_text": "H3", "label": "Ambiguous"},
        ]
    ).to_csv(path, index=False)

    df = load_labeled_dataset(str(path))

    assert len(df) == 2
    assert "Ambiguous" not in set(df["label"])


def test_make_train_test_split_is_stratified():
    df = pd.DataFrame(
        {
            "headline_text": [f"H{i}" for i in range(100)],
            "label": ["Informative"] * 80 + ["Clickbait"] * 20,
        }
    )

    train_df, test_df = make_train_test_split(df, test_size=0.2, seed=42)

    assert len(test_df) == 20
    assert len(train_df) == 80
    assert (test_df["label"] == "Clickbait").sum() == 4
    assert (test_df["label"] == "Informative").sum() == 16


def test_make_train_test_split_is_reproducible_with_same_seed():
    df = pd.DataFrame(
        {
            "headline_text": [f"H{i}" for i in range(50)],
            "label": ["Informative"] * 25 + ["Clickbait"] * 25,
        }
    )

    _, test1 = make_train_test_split(df, test_size=0.2, seed=42)
    _, test2 = make_train_test_split(df, test_size=0.2, seed=42)

    assert list(test1.index) == list(test2.index)


def test_held_out_outlet_split_partitions_by_outlet():
    df = pd.DataFrame(
        {
            "outlet": ["a", "a", "b", "b", "c"],
            "headline_text": ["H1", "H2", "H3", "H4", "H5"],
            "label": ["Informative"] * 5,
        }
    )

    train_df, test_df = held_out_outlet_split(df, "b")

    assert set(test_df["outlet"]) == {"b"}
    assert set(train_df["outlet"]) == {"a", "c"}
    assert len(test_df) == 2
    assert len(train_df) == 3
