from annotate.csv_io import read_csv_rows, append_csv_row

VERIFIED_FIELDS = ["url", "outlet", "source_style", "headline_text", "ai_label", "ai_rationale", "human_label", "overridden"]
VALID_KEYS = {"c": "Clickbait", "i": "Informative", "a": "Ambiguous"}


def load_verified_urls(path):
    try:
        rows = read_csv_rows(path)
    except FileNotFoundError:
        return set()
    return {row["url"] for row in rows}


def next_unverified_rows(pre_label_rows, verified_urls):
    return [row for row in pre_label_rows if row["url"] not in verified_urls]


def resolve_decision(key, ai_label):
    if key == "":
        return ai_label, False
    if key in VALID_KEYS:
        label = VALID_KEYS[key]
        return label, label != ai_label
    return None, None


def run(pre_labels_path="data/processed/pre_labels.csv", verified_path="data/processed/verified_labels.csv", input_fn=input, print_fn=print):
    pre_label_rows = read_csv_rows(pre_labels_path)
    verified_urls = load_verified_urls(verified_path)
    pending = next_unverified_rows(pre_label_rows, verified_urls)

    reviewed = 0
    overridden = 0
    total_already_done = len(verified_urls)

    for row in pending:
        print_fn(f"\n[{total_already_done + reviewed + 1}/{len(pre_label_rows)}]")
        print_fn(row["headline_text"])
        print_fn(f"AI suggested: {row['ai_label']} -- {row['ai_rationale']}")
        key = input_fn("[c]lickbait / [i]nformative / [a]mbiguous / Enter=accept / q=quit: ").strip().lower()

        if key == "q":
            break

        label, was_overridden = resolve_decision(key, row["ai_label"])
        if label is None:
            print_fn("Unrecognized input, skipping (re-run to retry this headline).")
            continue

        append_csv_row(
            {
                "url": row["url"],
                "outlet": row["outlet"],
                "source_style": row["source_style"],
                "headline_text": row["headline_text"],
                "ai_label": row["ai_label"],
                "ai_rationale": row["ai_rationale"],
                "human_label": label,
                "overridden": was_overridden,
            },
            verified_path,
            VERIFIED_FIELDS,
        )
        reviewed += 1
        if was_overridden:
            overridden += 1

    print_fn(f"\nReviewed {reviewed} headlines this session ({overridden} overridden).")
    print_fn(f"Total verified so far: {total_already_done + reviewed}/{len(pre_label_rows)}")


if __name__ == "__main__":
    run()
