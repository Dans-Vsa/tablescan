import json
from pathlib import Path

from tablescan.cli import main
from tablescan.loader import parse_csv, read_csv
from tablescan.profile import profile_table

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "people.csv"


def test_parse_pads_short_rows_and_names_blank_headers():
    t = parse_csv("a,,c\n1,2\n3,4,5\n")
    assert t.headers == ["a", "column_2", "c"]
    assert t.columns[2] == ["", "5"]
    assert t.n_rows == 2


def test_delimiter_sniffing():
    t = parse_csv("a;b\n1;2\n3;4\n")
    assert t.headers == ["a", "b"]


def test_empty_input_rejected():
    import pytest

    with pytest.raises(ValueError):
        parse_csv("   \n")


def test_profile_example():
    p = profile_table(read_csv(EXAMPLE))
    assert (p.n_rows, p.n_cols) == (10, 7)
    by = {c.name: c for c in p.columns}
    assert by["age"].dtype == "integer" and by["age"].missing == 1
    assert by["salary"].dtype == "float"
    assert by["joined"].dtype == "date" and by["joined"].min_value == "2017-04-18"
    assert by["active"].dtype == "boolean"
    assert by["city"].dtype == "text" and by["city"].top[0] == ["Jakarta", 4]
    assert by["age"].numeric["median"] == 34


def test_cli_text(capsys):
    assert main(["profile", str(EXAMPLE)]) == 0
    out = capsys.readouterr().out
    assert "Rows: 10" in out and "salary  [float]" in out


def test_cli_json(capsys):
    assert main(["profile", str(EXAMPLE), "--format", "json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["n_rows"] == 10
    assert data["columns"][2]["missing_pct"] == 10.0


def test_cli_missing_file(capsys):
    assert main(["profile", "nope.csv"]) == 1
    assert "error" in capsys.readouterr().err
