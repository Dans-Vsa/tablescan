"""Tiny dependency-free SVG chart builders."""

from __future__ import annotations

from html import escape
from typing import List, Sequence, Tuple

BAR_COLOR = "#4f7cff"


def _num(x: float) -> str:
    return f"{x:,.2f}".rstrip("0").rstrip(".") if x != int(x) else f"{int(x):,}"


def histogram_svg(edges: Sequence[float], counts: Sequence[int],
                  width: int = 360, height: int = 140) -> str:
    """Vertical bar chart for a numeric histogram."""
    pad_l, pad_b, pad_t = 8, 22, 8
    peak = max(counts) or 1
    n = len(counts)
    bw = (width - pad_l * 2) / n
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" '
             f'aria-label="histogram" class="chart">']
    for i, c in enumerate(counts):
        h = (height - pad_b - pad_t) * c / peak
        x = pad_l + i * bw
        y = height - pad_b - h
        title = f"{_num(edges[i])} to {_num(edges[i + 1])}: {c}"
        parts.append(f'<rect x="{x + 1:.1f}" y="{y:.1f}" width="{max(bw - 2, 1):.1f}" '
                     f'height="{h:.1f}" fill="{BAR_COLOR}" rx="2">'
                     f'<title>{escape(title)}</title></rect>')
    base = height - pad_b
    parts.append(f'<line x1="{pad_l}" y1="{base}" x2="{width - pad_l}" y2="{base}" '
                 f'stroke="currentColor" opacity="0.3"/>')
    parts.append(f'<text x="{pad_l}" y="{height - 6}" font-size="10" fill="currentColor">'
                 f'{escape(_num(edges[0]))}</text>')
    parts.append(f'<text x="{width - pad_l}" y="{height - 6}" font-size="10" '
                 f'text-anchor="end" fill="currentColor">{escape(_num(edges[-1]))}</text>')
    parts.append("</svg>")
    return "".join(parts)


def bars_svg(items: Sequence[Tuple[str, int]], width: int = 360, row: int = 22) -> str:
    """Horizontal bar chart for (label, count) pairs."""
    if not items:
        return ""
    label_w = 110
    peak = max(c for _, c in items) or 1
    height = row * len(items) + 4
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="top values" '
             f'class="chart">']
    for i, (label, c) in enumerate(items):
        y = 2 + i * row
        w = (width - label_w - 40) * c / peak
        text = label if len(label) <= 16 else label[:15] + "…"
        parts.append(f'<text x="{label_w - 6}" y="{y + 14}" font-size="11" '
                     f'text-anchor="end" fill="currentColor">{escape(text)}</text>')
        parts.append(f'<rect x="{label_w}" y="{y + 3}" width="{max(w, 1):.1f}" '
                     f'height="{row - 8}" fill="{BAR_COLOR}" rx="2">'
                     f'<title>{escape(label)}: {c}</title></rect>')
        parts.append(f'<text x="{label_w + w + 5:.1f}" y="{y + 14}" font-size="11" '
                     f'fill="currentColor">{c}</text>')
    parts.append("</svg>")
    return "".join(parts)


def corr_color(r: float) -> str:
    """Blue for positive, orange for negative, white at zero."""
    a = min(abs(r), 1.0)
    base = (79, 124, 255) if r >= 0 else (255, 140, 66)
    rgb = tuple(round(255 - (255 - ch) * a) for ch in base)
    return "#%02x%02x%02x" % rgb


def heatmap_svg(names: Sequence[str], matrix: List[List[float | None]],
                cell: int = 56) -> str:
    """Correlation heatmap; `matrix[i][j]` is r or None."""
    n = len(names)
    label_w = 90
    size = label_w + n * cell
    parts = [f'<svg viewBox="0 0 {size} {size}" role="img" '
             f'aria-label="correlation heatmap" class="chart heat">']
    for i, name in enumerate(names):
        short = name if len(name) <= 12 else name[:11] + "…"
        parts.append(f'<text x="{label_w - 6}" y="{label_w + i * cell + cell / 2 + 4}" '
                     f'font-size="11" text-anchor="end" fill="currentColor">'
                     f'{escape(short)}</text>')
        parts.append(f'<text x="{label_w + i * cell + cell / 2}" y="{label_w - 8}" '
                     f'font-size="11" text-anchor="middle" fill="currentColor">'
                     f'{escape(short)}</text>')
        for j in range(n):
            r = matrix[i][j]
            fill = "#e8e8e8" if r is None else corr_color(r)
            label = "n/a" if r is None else f"{r:+.2f}"
            x, y = label_w + j * cell, label_w + i * cell
            parts.append(f'<rect x="{x}" y="{y}" width="{cell - 2}" height="{cell - 2}" '
                         f'fill="{fill}" rx="3"><title>{escape(name)} vs '
                         f'{escape(names[j])}: {label}</title></rect>')
            parts.append(f'<text x="{x + cell / 2 - 1}" y="{y + cell / 2 + 3}" font-size="11" '
                         f'text-anchor="middle" fill="#1a1a1a">{label}</text>')
    parts.append("</svg>")
    return "".join(parts)
