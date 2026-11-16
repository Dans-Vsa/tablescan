"""Column type inference."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Iterable, List

from .loader import is_missing

INTEGER = "integer"
FLOAT = "float"
BOOLEAN = "boolean"
DATE = "date"
TEXT = "text"
EMPTY = "empty"

_BOOL_VALUES = {"true", "false", "yes", "no", "t", "f", "y", "n"}
_INT_RE = re.compile(r"^[+-]?\d+$")
_FLOAT_RE = re.compile(r"^[+-]?(\d+\.\d*|\.\d+|\d+)([eE][+-]?\d+)?$")
_DATE_FORMATS = ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S")


def parse_date(value: str) -> datetime | None:
    value = value.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _matches(values: List[str], kind: str) -> bool:
    if kind == BOOLEAN:
        return all(v.strip().lower() in _BOOL_VALUES for v in values)
    if kind == INTEGER:
        return all(_INT_RE.match(v.strip()) for v in values)
    if kind == FLOAT:
        return all(_FLOAT_RE.match(v.strip()) for v in values)
    if kind == DATE:
        return all(parse_date(v) is not None for v in values)
    return True


def infer_type(raw: Iterable[str]) -> str:
    """Infer the most specific type that fits every non-missing value."""
    values = [v for v in raw if not is_missing(v)]
    if not values:
        return EMPTY
    for kind in (BOOLEAN, INTEGER, FLOAT, DATE):
        if _matches(values, kind):
            return kind
    return TEXT
