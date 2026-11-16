"""Reading CSV files into a simple column-oriented structure."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

MISSING_TOKENS = {"", "na", "n/a", "nan", "null", "none", "-", "?"}


@dataclass
class Table:
    """A table stored column by column as raw strings."""

    headers: List[str]
    columns: List[List[str]] = field(default_factory=list)

    @property
    def n_rows(self) -> int:
        return len(self.columns[0]) if self.columns else 0

    @property
    def n_cols(self) -> int:
        return len(self.headers)


def is_missing(value: str) -> bool:
    """Return True when a raw cell should be treated as missing."""
    return value.strip().lower() in MISSING_TOKENS


def _sniff_delimiter(sample: str) -> str:
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def read_csv(path, delimiter: str | None = None, encoding: str = "utf-8-sig") -> Table:
    """Read a CSV file. Short rows are padded, long rows are truncated."""
    text = Path(path).read_text(encoding=encoding, newline="")
    return parse_csv(text, delimiter)


def parse_csv(text: str, delimiter: str | None = None) -> Table:
    """Parse CSV text into a Table."""
    if not text.strip():
        raise ValueError("CSV input is empty")
    delim = delimiter or _sniff_delimiter(text[:4096])
    rows = list(csv.reader(text.splitlines(), delimiter=delim))
    headers = [h.strip() or f"column_{i + 1}" for i, h in enumerate(rows[0])]
    columns: List[List[str]] = [[] for _ in headers]
    for row in rows[1:]:
        if not row:
            continue
        for i in range(len(headers)):
            columns[i].append(row[i] if i < len(row) else "")
    return Table(headers=headers, columns=columns)
