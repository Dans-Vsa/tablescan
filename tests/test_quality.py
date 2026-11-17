import json

import pytest

from tablescan import stats
from tablescan.cli import main
from tablescan.loader import parse_csv
from tablescan.profile import profile_table
from tablescan.quality import duplicate_rows, outlier_indices


def codes(csv_text):
    return [i.code for i in profile_table(parse_csv(csv_text)).issues]


def test_pearson_perfect_and_undefined():
    assert stats.pearson([1, 2, 3, 4], [2, 4, 6, 8]) == pytest.approx(1.0)
    assert stats.pearson([1, 2, 3, 4], [8, 6, 4, 2]) == pytest.approx(-1.0)
    assert stats.pearson([1, 1, 1], [1, 2, 3]) is None
    assert stats.pearson([1, 2], [1, 2]) is None


def test_iqr_bounds():
    lo, hi = stats.iqr_bounds([1, 2, 3, 4, 5, 6, 7, 8])
    assert lo < 1 and hi > 8


def test_duplicate_rows():
    t = parse_csv("a,b\n1,x\n2,y\n1,x\n1,x\n")
    assert duplicate_rows(t) == 2


def test_outliers():
    vals = [10, 11, 12, 11, 10, 12, 500]
    assert outlier_indices(vals) == [6]
    assert outlier_indices([1, 2, 3]) == []


def test_constant_and_empty_columns():
    found = codes("a,b,c\n1,x,\n2,x,\n3,x,\n")
    assert "constant_column" in found
    assert "empty_column" in found


def test_high_missing():
    rows = "\n".join(f"{i}," + ("" if i % 2 else "v") for i in range(10))
    assert "high_missing" in codes("n,t\n" + rows + "\n")


def test_high_cardinality_needs_enough_rows():
    small = "id\n" + "\n".join(f"u{i}" for i in range(5)) + "\n"
    big = "id\n" + "\n".join(f"u{i}" for i in range(30)) + "\n"
    assert "high_cardinality" not in codes(small)
    assert "high_cardinality" in codes(big)


def test_correlation_reported():
    rows = "\n".join(f"{i},{i * 3 + 1}" for i in range(10))
    prof = profile_table(parse_csv("x,y\n" + rows + "\n"))
    assert prof.correlations[0][:2] == ["x", "y"]
    assert "strong_correlation" in [i.code for i in prof.issues]


def test_clean_table_has_no_warnings():
    assert "duplicate_rows" not in codes("a,b\n1,x\n2,y\n3,z\n")


def _write(tmp_path, text):
    f = tmp_path / "d.csv"
    f.write_text(text, encoding="utf-8")
    return str(f)


def test_check_exit_codes(tmp_path, capsys):
    dirty = _write(tmp_path, "a,b\n1,x\n1,x\n2,y\n")
    assert main(["check", dirty]) == 2
    clean = _write(tmp_path, "a,b\n1,x\n2,y\n3,z\n")
    assert main(["check", clean]) == 0


def test_check_strict_and_json(tmp_path, capsys):
    f = _write(tmp_path, "a,b\n1,x\n2,x\n3,x\n")
    assert main(["check", f]) == 0
    assert main(["check", f, "--strict"]) == 2
    capsys.readouterr()
    main(["check", f, "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    assert data["passed"] is True
    assert data["issues"][0]["code"] == "constant_column"


def test_profile_json_includes_issues(tmp_path, capsys):
    f = _write(tmp_path, "a,b\n1,x\n1,x\n2,y\n")
    main(["profile", f, "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    assert any(i["code"] == "duplicate_rows" for i in data["issues"])
