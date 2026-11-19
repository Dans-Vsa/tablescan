from pathlib import Path

from tablescan import charts, stats
from tablescan.cli import main
from tablescan.loader import read_csv
from tablescan.profile import profile_table
from tablescan.render_html import correlation_matrix, render_html

EX = Path(__file__).resolve().parent.parent / "examples"


def test_histogram_counts_and_edges():
    edges, counts = stats.histogram([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], bins=5)
    assert len(edges) == 6 and sum(counts) == 10
    assert counts == [2, 2, 2, 2, 2]


def test_histogram_constant_values():
    edges, counts = stats.histogram([3, 3, 3])
    assert counts == [3] and edges[0] < 3 < edges[1]


def test_histogram_max_lands_in_last_bin():
    _, counts = stats.histogram([0, 10], bins=4)
    assert counts == [1, 0, 0, 1]


def test_corr_color_extremes():
    assert charts.corr_color(0) == "#ffffff"
    assert charts.corr_color(1) == "#4f7cff"
    assert charts.corr_color(-1) == "#ff8c42"


def test_bars_svg_escapes_labels():
    svg = charts.bars_svg([("<b>x</b>", 3)])
    assert "<b>" not in svg and "&lt;b&gt;" in svg


def test_profile_has_histogram_for_numeric_only():
    p = profile_table(read_csv(EX / "people.csv"))
    by = {c.name: c for c in p.columns}
    assert sum(by["age"].histogram["counts"]) == by["age"].count
    assert by["city"].histogram is None


def test_correlation_matrix_symmetric():
    p = profile_table(read_csv(EX / "messy.csv"))
    names, m = correlation_matrix(p)
    assert len(names) == len(m) >= 2
    assert all(m[i][i] == 1.0 for i in range(len(names)))
    assert all(m[i][j] == m[j][i] for i in range(len(names)) for j in range(len(names)))


def test_render_html_is_self_contained():
    html = render_html(profile_table(read_csv(EX / "messy.csv")), "T <1>")
    assert html.startswith("<!doctype html>")
    assert "&lt;1&gt;" in html and "<script" not in html
    assert "http://" not in html.replace("http://www.w3.org", "")
    assert html.count("<svg") >= 4 and "correlation heatmap" in html


def test_report_command(tmp_path, capsys):
    out = tmp_path / "r.html"
    assert main(["report", str(EX / "people.csv"), "-o", str(out)]) == 0
    assert "wrote" in capsys.readouterr().out
    assert "people.csv" in out.read_text(encoding="utf-8")


def test_report_default_path(tmp_path):
    csv = tmp_path / "d.csv"
    csv.write_text("a,b\n1,2\n2,4\n3,7\n", encoding="utf-8")
    assert main(["report", str(csv)]) == 0
    assert (tmp_path / "d.report.html").exists()


def test_report_bad_output(tmp_path, capsys):
    assert main(["report", str(EX / "people.csv"), "-o", str(tmp_path / "no" / "r.html")]) == 1
    assert "error" in capsys.readouterr().err
