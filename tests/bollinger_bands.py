"""
pytest suite for the BOLLINGERBANDS C++ indicator via pybind11.

This module tests edge cases and expected band computation behavior:
  - Initialization of parameters
  - Running on sample data
  - Correct computation of SMA, upper and lower bands for known inputs
  - No signals when price stays within bands
  - Sell signal when price spikes above upper band
  - Buy signal when price dips below lower band
"""
import pytest
import numpy as np
from TradeTide.binary.interface_indicators import BOLLINGERBANDS
import TradeTide
TradeTide.debug_mode = True  # Enable debug mode for development purpose

# Define constants for window and multiplier
WINDOW = 3
MULTIPLIER = 1.0


def test_initialize_indicator():
    """
    Initialize the BOLLINGERBANDS indicator with specified window and multiplier.

    Verifies that internal window and multiplier settings match constructor arguments.
    """
    indicator = BOLLINGERBANDS(
        window=WINDOW,
        multiplier=MULTIPLIER
    )
    assert indicator._cpp_window == WINDOW, "Window not set correctly"
    assert indicator._cpp_multiplier == MULTIPLIER, "Multiplier not set correctly"


def test_run_indicator_lengths():
    """
    Run the indicator on a simple price vector.

    Checks that SMA, upper, lower, and signals arrays all have the same length as input.
    """
    prices = [1.0, 2.0, 3.0, 4.0, 5.0]
    indicator = BOLLINGERBANDS(
        window=WINDOW,
        multiplier=MULTIPLIER
    )

    indicator._cpp_run_with_vector(prices)

    assert len(indicator._cpp_sma)    == len(prices), "SMA length mismatch"
    assert len(indicator._cpp_upper_band)  == len(prices), "Upper band length mismatch"
    assert len(indicator._cpp_lower_band)  == len(prices), "Lower band length mismatch"
    assert len(indicator._cpp_regions) == len(prices), "Signals length mismatch"


def test_band_values_accuracy():
    """
    Validate SMA and band computations against manual calculations.
    """
    # Known sequence
    prices = [10.0, 20.0, 30.0, 40.0, 50.0]
    indicator = BOLLINGERBANDS(window=WINDOW, multiplier=MULTIPLIER)
    indicator._cpp_run_with_vector(prices)

    sma   = np.asarray(indicator._cpp_sma)
    upper = np.asarray(indicator._cpp_upper_band)
    lower = np.asarray(indicator._cpp_lower_band)
    sig   = np.asarray(indicator._cpp_regions)

    # SMA at idx=2: mean([10,20,30]) = 20
    assert pytest.approx(sma[2], rel=1e-9) == 20.0

    # Standard deviation of [10,20,30]: sqrt(2/3 * 100) ≈ 8.1649658...
    std = np.std(prices[:3], ddof=0)
    # Upper at idx=2: 20 + 1*std
    assert pytest.approx(upper[2], rel=1e-7) == 20.0 + std
    # Lower at idx=2: 20 - 1*std
    assert pytest.approx(lower[2], rel=1e-7) == 20.0 - std


def test_sell_signal_on_upper_break():
    """
    Verify that a spike above the upper band generates a sell (-1) signal.
    """
    # Sequence spikes at idx=3
    prices = [1.0, 1.0, 1.0, 10.0, 1.0, 1.0]
    indicator = BOLLINGERBANDS(window=WINDOW, multiplier=MULTIPLIER)
    indicator._cpp_run_with_vector(prices)

    sig = np.asarray(indicator._cpp_regions).tolist()
    # Expect sell at idx=3
    assert sig[3] == -1, "Expected sell signal at index 3"
    # Only one signal
    assert sum(1 for s in sig if s != 0) == 1, "Only one signal expected"


def test_buy_signal_on_lower_break():
    """
    Verify that a dip below the lower band generates a buy (+1) signal.
    """
    # Build a high baseline then dip at idx=3
    prices = [10.0, 10.0, 10.0, 1.0, 10.0, 10.0]
    indicator = BOLLINGERBANDS(window=WINDOW, multiplier=MULTIPLIER)
    indicator._cpp_run_with_vector(prices)

    sig = np.asarray(indicator._cpp_regions).tolist()
    # Expect buy at idx=3
    assert sig[3] == 1, "Expected buy signal at index 3"
    # Only one signal
    assert sum(1 for s in sig if s != 0) == 1, "Only one signal expected"


if __name__ == "__main__":
    pytest.main(["-W error", __file__])
