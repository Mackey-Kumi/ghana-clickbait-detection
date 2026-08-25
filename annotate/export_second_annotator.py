import random

from annotate.csv_io import read_csv_rows, write_csv_rows
from annotate.sampling import stratified_sample

SUBSET_FIELDS = ["id", "headline_text", "label"]
MAPPING_FIELDS = ["id", "url", "outlet", "source_style"]


def build_subset(rows, target_total, seed=42):
    outlet_counts = {}
    for row in rows:
        outlet_counts[row["outlet"]] = outlet_counts.get(row["outlet"], 0) + 1

    sizes = stratified_sample(outlet_counts, target_total)

    by_outlet = {}
    for row in rows:
        by_outlet.setdefault(row["outlet"], []).append(row)

    rng = random.Random(seed)
    selected = []
    for outlet, size in sizes.items():
        selected.extend(rng.sample(by_outlet[outlet], size))
    rng.shuffle(selected)

    subset_rows = []
    mapping_rows = []
    for i, row in enumerate(selected, start=1):
        item_id = f"H{i:03d}"
        subset_rows.append({"id": item_id, "headline_text": row["headline_text"], "label": ""})
        mapping_rows.append({"id": item_id, "url": row["url"], "outlet": row["outlet"], "source_style": row["source_style"]})
    return subset_rows, mapping_rows


if __name__ == "__main__":
    rows = read_csv_rows("data/raw/headlines_combined.csv")
    subset_rows, mapping_rows = build_subset(rows, target_total=250)
    write_csv_rows(subset_rows, "data/processed/second_annotator_subset.csv", SUBSET_FIELDS)
    write_csv_rows(mapping_rows, "data/processed/second_annotator_mapping.csv", MAPPING_FIELDS)
    print(f"Wrote {len(subset_rows)} headlines to data/processed/second_annotator_subset.csv")
