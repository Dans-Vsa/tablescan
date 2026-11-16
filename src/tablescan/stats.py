"""Pure-Python statistics helpers."""

from __future__ import annotations

import math
from collections import Counter
from typing import Dict, List, Sequence, Tuple


def mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs)


def variance(xs: Sequence[float]) -> float:
    """Sample variance (n - 1). Returns 0.0 for fewer than two values."""
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def std(xs: Sequence[float]) -> float:
    return math.sqrt(variance(xs))


def quantile(sorted_xs: Sequence[float], q: float) -> float:
    """Linear-interpolated quantile of an already sorted sequence."""
    if not sorted_xs:
        raise ValueError("quantile of empty sequence")
    pos = (len(sorted_xs) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return float(sorted_xs[lo])
    frac = pos - lo
    return sorted_xs[lo] * (1 - frac) + sorted_xs[hi] * frac


def skewness(xs: Sequence[float]) -> float:
    """Adjusted Fisher-Pearson skewness; 0.0 when undefined."""
    n = len(xs)
    if n < 3:
        return 0.0
    s = std(xs)
    if s == 0:
        return 0.0
    m = mean(xs)
    return (n / ((n - 1) * (n - 2))) * sum(((x - m) / s) ** 3 for x in xs)


def numeric_summary(xs: Sequence[float]) -> Dict[str, float]:
    """Describe a numeric sample."""
    ordered = sorted(xs)
    return {
        "min": float(ordered[0]),
        "q1": quantile(ordered, 0.25),
        "median": quantile(ordered, 0.5),
        "q3": quantile(ordered, 0.75),
        "max": float(ordered[-1]),
        "mean": mean(ordered),
        "std": std(ordered),
        "skew": skewness(ordered),
    }


def top_values(values: Sequence[str], n: int = 5) -> List[Tuple[str, int]]:
    """Most common values; ties keep first-seen order."""
    return Counter(values).most_common(n)
