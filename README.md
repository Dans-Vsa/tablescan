# tablescan

A zero-dependency CSV profiler written in pure Python. Point it at a CSV file and get column types, descriptive statistics and (soon) data-quality warnings and a shareable HTML report - no pandas required.

> Status: **v0.1.0 - work in progress** (milestone 1 of 4).

## Features

- [x] CSV loading with delimiter auto-detection (`,` `;` tab `|`), BOM handling, ragged-row padding
- [x] Column type inference: integer, float, boolean, date, text, empty
- [x] Missing-value detection (`""`, `NA`, `null`, `NaN`, `-`, `?`, ...)
- [x] Numeric statistics: min, quartiles, median, max, mean, std, skewness
- [x] Top values, unique counts, date ranges, average text length
- [x] Plain-text and JSON output
- [ ] Data-quality checks: duplicates, outliers, constant / high-cardinality columns, correlations (milestone 2)
- [ ] Self-contained HTML report with SVG charts (milestone 3)
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
```

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
  render_text.py  plain-text report
  cli.py          command-line interface
tests/            pytest suite
examples/         sample CSV files
```

## License

MIT
