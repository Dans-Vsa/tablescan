"""Plain-text rendering of a TableProfile."""

from __future__ import annotations

from typing import List

from .profile import ColumnProfile, TableProfile


def _fmt(x: float) -> str:
    return f"{x:,.2f}".rstrip("0").rstrip(".") if x != int(x) else f"{int(x):,}"


def _column_lines(col: ColumnProfile) -> List[str]:
    lines = [
        f"{col.name}  [{col.dtype}]",
        f"  values: {col.count}   missing: {col.missing} ({col.missing_pct}%)   unique: {col.unique}",
    ]
    if col.numeric:
        n = col.numeric
        lines.append(
            f"  min {_fmt(n['min'])} | q1 {_fmt(n['q1'])} | median {_fmt(n['median'])} | "
            f"q3 {_fmt(n['q3'])} | max {_fmt(n['max'])}"
        )
        lines.append(f"  mean {_fmt(n['mean'])} | std {_fmt(n['std'])} | skew {n['skew']:.2f}")
    elif col.min_value:
        lines.append(f"  range: {col.min_value} -> {col.max_value}")
    elif col.avg_length is not None:
        lines.append(f"  avg length: {col.avg_length}")
    if col.top and col.dtype not in ("integer", "float"):
        top = ", ".join(f"{v} ({c})" for v, c in col.top[:3])
        lines.append(f"  top: {top}")
    return lines


def render_text(profile: TableProfile) -> str:
    out = [f"Rows: {profile.n_rows}   Columns: {profile.n_cols}", "=" * 40]
    for col in profile.columns:
        out.extend(_column_lines(col))
        out.append("")
    return "\n".join(out).rstrip() + "\n"
