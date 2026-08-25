import sys

from annotate.csv_io import read_csv_rows, read_table_rows


def cohens_kappa(labels_a, labels_b):
    n = len(labels_a)
    categories = sorted(set(labels_a) | set(labels_b))

    po = sum(1 for a, b in zip(labels_a, labels_b) if a == b) / n

    freq_a = {c: labels_a.count(c) / n for c in categories}
    freq_b = {c: labels_b.count(c) / n for c in categories}
    pe = sum(freq_a[c] * freq_b[c] for c in categories)

    if pe == 1:
        return 1.0
    return (po - pe) / (1 - pe)


def load_paired_labels(verified_path, mapping_path, second_annotator_completed_path):
    verified_rows = {row["url"]: row["human_label"] for row in read_csv_rows(verified_path)}
    mapping_rows = {row["id"]: row["url"] for row in read_csv_rows(mapping_path)}
    second_rows = read_table_rows(second_annotator_completed_path)

    labels_a = []
    labels_b = []
    for row in second_rows:
        url = mapping_rows[row["id"]]
        if url in verified_rows and row["label"]:
            labels_a.append(verified_rows[url])
            labels_b.append(row["label"])
    return labels_a, labels_b


def main():
    second_annotator_completed_path = sys.argv[1]
    labels_a, labels_b = load_paired_labels(
        "data/processed/verified_labels.csv",
        "data/processed/second_annotator_mapping.csv",
        second_annotator_completed_path,
    )
    score = cohens_kappa(labels_a, labels_b)
    print(f"Paired items: {len(labels_a)}")
    print(f"Cohen's Kappa: {score:.3f}")
    agree = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
    print(f"Raw agreement: {agree}/{len(labels_a)} ({agree / len(labels_a):.1%})")


if __name__ == "__main__":
    main()
