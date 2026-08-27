import pandas as pd
from sklearn.model_selection import train_test_split

LABELED_PATH_DEFAULT = "data/processed/annotated_headlines.csv"


def load_labeled_dataset(path=LABELED_PATH_DEFAULT):
    df = pd.read_csv(path)
    return df[df["label"] != "Ambiguous"].reset_index(drop=True)


def make_train_test_split(df, test_size=0.2, seed=42):
    return train_test_split(df, test_size=test_size, random_state=seed, stratify=df["label"])


def held_out_outlet_split(df, held_out_outlet):
    train_df = df[df["outlet"] != held_out_outlet].reset_index(drop=True)
    test_df = df[df["outlet"] == held_out_outlet].reset_index(drop=True)
    return train_df, test_df
