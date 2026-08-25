from annotate.csv_io import read_csv_rows, write_csv_rows

PRE_LABEL_FIELDS = ["url", "outlet", "source_style", "headline_text", "ai_label", "ai_rationale"]


def build_template(source_rows):
    return [
        {
            "url": row["url"],
            "outlet": row["outlet"],
            "source_style": row["source_style"],
            "headline_text": row["headline_text"],
            "ai_label": "",
            "ai_rationale": "",
        }
        for row in source_rows
    ]


if __name__ == "__main__":
    source_rows = read_csv_rows("data/raw/headlines_combined.csv")
    template_rows = build_template(source_rows)
    write_csv_rows(template_rows, "data/processed/pre_labels.csv", PRE_LABEL_FIELDS)
    print(f"Wrote {len(template_rows)} rows to data/processed/pre_labels.csv")
