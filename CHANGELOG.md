# Changelog

## 1.0.0 - 2026-11-20
- Read CSV from stdin with `-` as the file name.
- New `--encoding` option for non-UTF-8 files.
- Fix: quoted cells containing newlines are no longer split into separate rows.
- GitHub Actions CI (Linux + Windows, Python 3.9 and 3.12).

## 0.3.0 - 2026-11-19
- `report` command: self-contained HTML report with SVG charts.

## 0.2.0 - 2026-11-17
- Data-quality checks and the `check` command with CI-friendly exit codes.

## 0.1.0 - 2026-11-16
- CSV loader, type inference, statistics and `profile` command.
