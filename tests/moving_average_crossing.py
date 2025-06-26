"""
pytest suite for the MOVINGAVERAGECROSSING C++ indicator via pybind11.

This module tests edge cases and expected crossover behavior:
  - Initialization of parameters
  - Running on sample data
  - Correct generation of signals for a falling-then-rising series
  - Death cross detection for rising-then-falling series
  - Moving-average value correctness for known inputs
"""
import pytest
import numpy as np
from TradeTide.binary.interface_indicators import MOVINGAVERAGECROSSING

# Define constants for window sizes
SHORT_WINDOW = 3
LONG_WINDOW = 5


def test_initialize_indicator():
    """
    Initialize the MOVINGAVERAGECROSSING indicator with specified windows.

    Verifies that internal window settings match constructor arguments.
    """
    indicator = MOVINGAVERAGECROSSING(
        short_window=SHORT_WINDOW,
        long_window=LONG_WINDOW
    )
    assert indicator._cpp_short_window == SHORT_WINDOW, "Short window not set correctly"
    assert indicator._cpp_long_window == LONG_WINDOW, "Long window not set correctly"


def test_run_indicator():
    """
    Run the indicator on a simple increasing price vector.

    Checks that output arrays have the same length as input.
    """
    prices = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    indicator = MOVINGAVERAGECROSSING(
        short_window=SHORT_WINDOW,
        long_window=LONG_WINDOW
    )
    indicator._cpp_run_with_vector(prices)

    assert len(indicator._cpp_short_moving_average) == len(prices), "Short MA length mismatch"
    assert len(indicator._cpp_long_moving_average) == len(prices), "Long MA length mismatch"
    assert len(indicator._cpp_regions) == len(prices), "Signals length mismatch"


def test_signals_golden_cross():
    """
    Verify golden cross for a falling-then-rising series.
    """
    prices = [5.0, 4.0, 3.0, 2.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    indicator = MOVINGAVERAGECROSSING(short_window=SHORT_WINDOW, long_window=LONG_WINDOW)
    indicator._cpp_run_with_vector(prices)
    signals = np.asarray(indicator._cpp_regions).tolist()

    # Expect golden cross at index 7
    assert signals[7] == 1, "Expected golden cross signal at index 7"


def test_signals_death_cross():
    """
    Verify death cross for a rising-then-falling series.
    """
    prices = [1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 1.0]
    indicator = MOVINGAVERAGECROSSING(short_window=SHORT_WINDOW, long_window=LONG_WINDOW)
    indicator._cpp_run_with_vector(prices)
    signals = np.asarray(indicator._cpp_regions).tolist()

    # Expect death cross at index 7
    assert signals[7] == -1, "Expected death cross signal at index 7"


def test_ma_values_accuracy():
    """
    Validate moving-average computations against manual calculations.
    """
    # Use a known short sequence
    prices = [10.0, 20.0, 30.0, 40.0, 50.0]
    indicator = MOVINGAVERAGECROSSING(short_window=3, long_window=5)
    indicator._cpp_run_with_vector(prices)

    short_ma = np.asarray(indicator._cpp_short_moving_average)
    long_ma = np.asarray(indicator._cpp_long_moving_average)

    # short_window=3: first defined at index 2: mean([10,20,30]) = 20
    assert pytest.approx(short_ma[2], rel=1e-9) == 20.0
    # at index 3: mean([20,30,40]) = 30
    assert pytest.approx(short_ma[3], rel=1e-9) == 30.0

    # long_window=5: first defined at index 4: mean([10,20,30,40,50]) = 30
    assert pytest.approx(long_ma[4], rel=1e-9) == 30.0

    # Signals: none expected as short never crosses long
    signals = np.asarray(indicator._cpp_regions)


if __name__ == "__main__":
    pytest.main(["-W error", __file__])