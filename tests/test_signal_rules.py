import numpy as np
import pytest

from TradeTide.signal_rules import all_of, any_of, weighted


def test_all_of_requires_unanimous_direction():
    result = all_of([1, 1, -1, 0], [1, 0, -1, -1])
    np.testing.assert_array_equal(result, [1, 0, -1, 0])


def test_any_of_requires_no_opposing_direction():
    result = any_of([1, 0, -1, 1], [0, -1, -1, -1])
    np.testing.assert_array_equal(result, [1, -1, -1, 0])


def test_weighted_applies_weights_and_threshold():
    result = weighted([1, 1, -1], [-1, 1, -1], weights=[2, 1], threshold=0.5)
    np.testing.assert_array_equal(result, [1, 1, -1])


@pytest.mark.parametrize(
    ("call", "message"),
    [
        (lambda: all_of(), "one or more"),
        (lambda: any_of([2]), "-1, 0, or 1"),
        (lambda: weighted([1], [1], weights=[1]), "exactly one"),
        (lambda: weighted([1], weights=[1], threshold=-1), "non-negative"),
    ],
)
def test_invalid_signal_rules_raise_clear_errors(call, message):
    with pytest.raises(ValueError, match=message):
        call()
