# tablescan

A zero-dependency CSV profiler written in pure Python. Point it at a CSV file and get column types, descriptive statistics and (soon) data-quality warnings and a shareable HTML report - no pandas required.

> Status: **v0.3.0 - work in progress** (milestone 3 of 4).

## Features

- [x] CSV loading with delimiter auto-detection (`,` `;` tab `|`), BOM handling, ragged-row padding
- [x] Column type inference: integer, float, boolean, date, text, empty
- [x] Missing-value detection (`""`, `NA`, `null`, `NaN`, `-`, `?`, ...)
- [x] Numeric statistics: min, quartiles, median, max, mean, std, skewness
- [x] Top values, unique counts, date ranges, average text length
- [x] Plain-text and JSON output
- [x] Data-quality checks: duplicate rows, IQR outliers, empty / constant / high-missing / high-cardinality columns, strong correlations
- [x] `check` command with CI-friendly exit codes (`0` ok, `2` warnings, `--strict` also fails on info)
- [x] Self-contained HTML report: histograms, top-value bars, correlation heatmap, light/dark theme, no scripts or external assets
- [x] `report` command (`-o`, `--title`)
- [ ] CI, changelog, v1.0.0 (milestone 4)

## Tech stack

Python 3.9+, standard library only. `pytest` for tests.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## Usage

```powershell
.\.venv\Scripts\tablescan.exe profile examples\people.csv
.\.venv\Scripts\tablescan.exe profile examples\people.csv --format json
.\.venv\Scripts\tablescan.exe profile data.csv --delimiter ";"
.\.venv\Scripts\tablescan.exe check examples\messy.csv
.\.venv\Scripts\tablescan.exe check examples\messy.csv --format json --strict
```

```powershell
.\.venv\Scripts	ablescan.exe report examples\messy.csv
.\.venv\Scripts	ablescan.exe report data.csv -o outeport.html --title "Sales data"
```

`report` writes a single HTML file (default `<file>.report.html`) with inline CSS and SVG charts; open it in any browser or attach it to an email. See [examples/messy.report.html](examples/messy.report.html).

`profile` now ends with a data-quality section; `check` prints only that section and exits with code `2` when warnings are found.

Example `check` output:

```
Data quality: 3 issue(s)
----------------------------------------
  WARNING 1 duplicate row(s) found
  WARNING [units] 1 outlier(s) outside the 1.5xIQR fences
  INFO    units and revenue are strongly correlated (r = +1.00)
```

| Check | Level | Rule |
|-------|-------|------|
| duplicate_rows | warning | row identical to an earlier row |
| outliers | warning | numeric value outside Q1-1.5xIQR / Q3+1.5xIQR |
| empty_column | warning | no non-missing values |
| high_missing | warning | >= 30% missing |
| constant_column | info | one distinct value |
| high_cardinality | info | text column, >= 20 rows, >= 90% unique |
| strong_correlation | info | Pearson abs(r) >= 0.8 between numeric columns |

Example output:

```
Rows: 10   Columns: 7
========================================
age  [integer]
  values: 9   missing: 1 (10.0%)   unique: 9
  min 23 | q1 29 | median 34 | q3 41 | max 52
  mean 35.78 | std 9.23 | skew 0.46
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Project structure

```
src/tablescan/
  loader.py       CSV parsing into a column-oriented Table
  types.py        column type inference
  stats.py        pure-Python statistics helpers
  profile.py      ColumnProfile / TableProfile builders
  quality.py      data-quality checks (duplicates, outliers, correlations)
  render_text.py  plain-text report
  charts.py       dependency-free SVG chart builders
  render_html.py  self-contained HTML report
  cli.py          command-line interface
tests/            pytest suite
examples/         sample CSV files
```

## License

MIT
