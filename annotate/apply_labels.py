from annotate.csv_io import read_csv_rows, write_csv_rows
from annotate.build_pre_label_template import PRE_LABEL_FIELDS


def merge_labels(rows, updates):
    for row in rows:
        if row["url"] in updates:
            label, rationale = updates[row["url"]]
            row["ai_label"] = label
            row["ai_rationale"] = rationale
    return rows


def apply_labels(path, updates):
    rows = read_csv_rows(path)
    rows = merge_labels(rows, updates)
    write_csv_rows(rows, path, PRE_LABEL_FIELDS)
    return rows
