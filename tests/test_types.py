import pytest

from tablescan.types import BOOLEAN, DATE, EMPTY, FLOAT, INTEGER, TEXT, infer_type


@pytest.mark.parametrize(
    "values,expected",
    [
        (["1", "2", "-3"], INTEGER),
        (["1.5", "2", "3e2"], FLOAT),
        (["true", "False", "yes"], BOOLEAN),
        (["2020-01-02", "2021-12-31"], DATE),
        (["hello", "1"], TEXT),
        (["", "NA", "null"], EMPTY),
        (["1", "", "3"], INTEGER),
    ],
)
def test_infer_type(values, expected):
    assert infer_type(values) == expected
