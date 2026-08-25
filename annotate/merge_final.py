from annotate.csv_io import read_csv_rows, write_csv_rows

FINAL_FIELDS = ["url", "outlet", "source_style", "headline_text", "label"]


def build_final_rows(verified_rows):
    return [
        {
            "url": row["url"],
            "outlet": row["outlet"],
            "source_style": row["source_style"],
            "headline_text": row["headline_text"],
            "label": row["human_label"],
        }
        for row in verified_rows
    ]


if __name__ == "__main__":
    verified_rows = read_csv_rows("data/processed/verified_labels.csv")
    final_rows = build_final_rows(verified_rows)
    write_csv_rows(final_rows, "data/processed/annotated_headlines.csv", FINAL_FIELDS)
    print(f"Wrote {len(final_rows)} rows to data/processed/annotated_headlines.csv")
