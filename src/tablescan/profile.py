"""Build a profile (types + statistics) for a table."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from . import quality, stats
from .loader import Table, is_missing
from .types import BOOLEAN, DATE, EMPTY, FLOAT, INTEGER, TEXT, infer_type, parse_date


@dataclass
class ColumnProfile:
    name: str
    dtype: str
    count: int
    missing: int
    unique: int
    top: List[List[Any]] = field(default_factory=list)
    numeric: Optional[Dict[str, float]] = None
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    avg_length: Optional[float] = None
    histogram: Optional[Dict[str, List[float]]] = None

    @property
    def missing_pct(self) -> float:
        total = self.count + self.missing
        return round(100.0 * self.missing / total, 2) if total else 0.0


@dataclass
class TableProfile:
    n_rows: int
    n_cols: int
    columns: List[ColumnProfile]
    issues: List[quality.Issue] = field(default_factory=list)
    correlations: List[List[Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        for col, src in zip(data["columns"], self.columns):
            col["missing_pct"] = src.missing_pct
        return data


def _to_number(value: str) -> float:
    return float(value.strip())


def profile_column(name: str, raw: List[str]) -> ColumnProfile:
    dtype = infer_type(raw)
    present = [v.strip() for v in raw if not is_missing(v)]
    col = ColumnProfile(
        name=name,
        dtype=dtype,
        count=len(present),
        missing=len(raw) - len(present),
        unique=len(set(present)),
    )
    if dtype == EMPTY:
        return col
    col.top = [[v, c] for v, c in stats.top_values(present)]
    if dtype in (INTEGER, FLOAT):
        nums = [_to_number(v) for v in present]
        col.numeric = stats.numeric_summary(nums)
        edges, counts = stats.histogram(nums)
        col.histogram = {"edges": edges, "counts": counts}
    elif dtype == DATE:
        dates = sorted(d for d in (parse_date(v) for v in present) if d)
        col.min_value = dates[0].date().isoformat()
        col.max_value = dates[-1].date().isoformat()
    elif dtype == TEXT:
        col.avg_length = round(sum(len(v) for v in present) / len(present), 2)
    return col


def profile_table(table: Table) -> TableProfile:
    cols = [profile_column(h, c) for h, c in zip(table.headers, table.columns)]
    issues, corr = quality.analyze(table, cols)
    return TableProfile(
        n_rows=table.n_rows,
        n_cols=table.n_cols,
        columns=cols,
        issues=issues,
        correlations=[list(c) for c in corr],
    )
