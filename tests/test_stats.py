import math

import pytest

from tablescan import stats


def test_mean_and_std():
    xs = [2, 4, 4, 4, 5, 5, 7, 9]
    assert stats.mean(xs) == 5
    assert stats.std(xs) == pytest.approx(2.13809, rel=1e-4)


def test_quantile_interpolates():
    xs = [1, 2, 3, 4]
    assert stats.quantile(xs, 0.5) == 2.5
    assert stats.quantile(xs, 0) == 1
    assert stats.quantile(xs, 1) == 4


def test_quantile_empty_raises():
    with pytest.raises(ValueError):
        stats.quantile([], 0.5)


def test_skewness_symmetric_is_zero():
    assert stats.skewness([1, 2, 3, 4, 5]) == pytest.approx(0.0, abs=1e-9)


def test_skewness_right_tail_positive():
    assert stats.skewness([1, 1, 1, 2, 10]) > 0


def test_single_value_std_zero():
    assert stats.std([5]) == 0.0
    assert not math.isnan(stats.skewness([5, 5, 5]))


def test_top_values():
    assert stats.top_values(["a", "b", "a", "c", "a", "b"], 2) == [("a", 3), ("b", 2)]
