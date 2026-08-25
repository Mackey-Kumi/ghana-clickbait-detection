from annotate.csv_io import read_csv_rows, write_csv_rows, append_csv_row


def test_write_then_read_round_trip(tmp_path):
    path = str(tmp_path / "out.csv")
    rows = [
        {"a": "1", "b": "x"},
        {"a": "2", "b": "y"},
    ]
    write_csv_rows(rows, path, fieldnames=["a", "b"])
    result = read_csv_rows(path)
    assert result == rows


def test_append_csv_row_creates_file_with_header(tmp_path):
    path = str(tmp_path / "out.csv")
    append_csv_row({"a": "1", "b": "x"}, path, fieldnames=["a", "b"])
    result = read_csv_rows(path)
    assert result == [{"a": "1", "b": "x"}]


def test_append_csv_row_appends_without_duplicate_header(tmp_path):
    path = str(tmp_path / "out.csv")
    append_csv_row({"a": "1", "b": "x"}, path, fieldnames=["a", "b"])
    append_csv_row({"a": "2", "b": "y"}, path, fieldnames=["a", "b"])
    result = read_csv_rows(path)
    assert result == [{"a": "1", "b": "x"}, {"a": "2", "b": "y"}]
