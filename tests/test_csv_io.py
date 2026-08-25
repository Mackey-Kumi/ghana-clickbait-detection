from openpyxl import Workbook

from annotate.csv_io import read_csv_rows, write_csv_rows, append_csv_row, read_xlsx_rows, read_table_rows


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


def _write_xlsx(path, header, data_rows):
    wb = Workbook()
    ws = wb.active
    ws.append(header)
    for row in data_rows:
        ws.append(row)
    wb.save(path)


def test_read_xlsx_rows_returns_dicts_keyed_by_header(tmp_path):
    path = str(tmp_path / "out.xlsx")
    _write_xlsx(path, ["a", "b"], [["1", "x"], ["2", "y"]])
    result = read_xlsx_rows(path)
    assert result == [{"a": "1", "b": "x"}, {"a": "2", "b": "y"}]


def test_read_xlsx_rows_skips_fully_blank_rows(tmp_path):
    path = str(tmp_path / "out.xlsx")
    _write_xlsx(path, ["a", "b"], [["1", "x"], [None, None], ["2", "y"]])
    result = read_xlsx_rows(path)
    assert result == [{"a": "1", "b": "x"}, {"a": "2", "b": "y"}]


def test_read_table_rows_dispatches_on_extension(tmp_path):
    csv_path = str(tmp_path / "out.csv")
    write_csv_rows([{"a": "1", "b": "x"}], csv_path, fieldnames=["a", "b"])
    xlsx_path = str(tmp_path / "out.xlsx")
    _write_xlsx(xlsx_path, ["a", "b"], [["1", "x"]])

    assert read_table_rows(csv_path) == [{"a": "1", "b": "x"}]
    assert read_table_rows(xlsx_path) == [{"a": "1", "b": "x"}]
