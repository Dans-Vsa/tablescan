"""Data-quality checks: duplicates, outliers, constants, cardinality, correlations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from . import stats
from .loader import Table, is_missing
from .types import FLOAT, INTEGER, TEXT, EMPTY

WARNING = "warning"
INFO = "info"

HIGH_MISSING_PCT = 30.0
HIGH_CARDINALITY_RATIO = 0.9
MIN_ROWS_FOR_CARDINALITY = 20
CORRELATION_THRESHOLD = 0.8


@dataclass
class Issue:
    severity: str
    code: str
    message: str
    column: str | None = None


def duplicate_rows(table: Table) -> int:
    """Count rows that exactly repeat an earlier row."""
    seen = set()
    dups = 0
    for row in zip(*table.columns):
        key = tuple(c.strip() for c in row)
        if key in seen:
            dups += 1
        else:
            seen.add(key)
    return dups


def outlier_indices(values: List[float], k: float = 1.5) -> List[int]:
    """Indices of values outside the Tukey fences."""
    if len(values) < 4:
        return []
    lo, hi = stats.iqr_bounds(values, k)
    return [i for i, v in enumerate(values) if v < lo or v > hi]


def numeric_pairs(table: Table, dtypes: Dict[str, str]) -> List[Tuple[str, str, float]]:
    """Pearson correlation for every pair of numeric columns (pairwise complete rows)."""
    names = [h for h in table.headers if dtypes[h] in (INTEGER, FLOAT)]
    cols = {h: table.columns[table.headers.index(h)] for h in names}
    out = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            xs, ys = [], []
            for va, vb in zip(cols[a], cols[b]):
                if not is_missing(va) and not is_missing(vb):
                    xs.append(float(va))
                    ys.append(float(vb))
            r = stats.pearson(xs, ys)
            if r is not None:
                out.append((a, b, round(r, 4)))
    return out


def analyze(table: Table, columns) -> Tuple[List[Issue], List[Tuple[str, str, float]]]:
    """Run all checks. `columns` is the list of ColumnProfile objects."""
    issues: List[Issue] = []
    dtypes = {c.name: c.dtype for c in columns}

    dups = duplicate_rows(table)
    if dups:
        issues.append(Issue(WARNING, "duplicate_rows", f"{dups} duplicate row(s) found"))

    for col, raw in zip(columns, table.columns):
        total = col.count + col.missing
        if col.dtype == EMPTY:
            issues.append(Issue(WARNING, "empty_column", "column has no values", col.name))
            continue
        if col.missing_pct >= HIGH_MISSING_PCT:
            issues.append(Issue(WARNING, "high_missing",
                                f"{col.missing_pct}% of values are missing", col.name))
        if col.unique == 1 and total > 1:
            issues.append(Issue(INFO, "constant_column",
                                "column has a single distinct value", col.name))
        if (col.dtype == TEXT and col.count >= MIN_ROWS_FOR_CARDINALITY
                and col.unique / col.count >= HIGH_CARDINALITY_RATIO):
            issues.append(Issue(INFO, "high_cardinality",
                                f"{col.unique} distinct values in {col.count} rows (id-like?)",
                                col.name))
        if col.dtype in (INTEGER, FLOAT):
            present = [float(v) for v in raw if not is_missing(v)]
            n_out = len(outlier_indices(present))
            if n_out:
                issues.append(Issue(WARNING, "outliers",
                                    f"{n_out} outlier(s) outside the 1.5xIQR fences", col.name))

    corr = numeric_pairs(table, dtypes)
    for a, b, r in corr:
        if abs(r) >= CORRELATION_THRESHOLD:
            issues.append(Issue(INFO, "strong_correlation",
                                f"{a} and {b} are strongly correlated (r = {r:+.2f})"))
    return issues, corr
