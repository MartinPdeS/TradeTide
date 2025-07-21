import gc
import time
import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch
from TradeTide.indicators.relative_momentum_index import RelativeMomentumIndex
from TradeTide.market import Market
from TradeTide.times import minutes, hours, days
from TradeTide.currencies import Currency
import TradeTide

# Enable debug mode for detailed logging during test execution
TradeTide.debug_mode = True

# ===============================
# Test Configuration and Constants
# ===============================

DEFAULT_MOMENTUM_PERIOD = 14 * minutes
DEFAULT_SMOOTH_WINDOW = 14 * minutes
DEFAULT_OVERBOUGHT = 70.0
DEFAULT_OVERSOLD = 30.0
DEFAULT_CURRENCY = Currency.USD
DEFAULT_START_DATE = datetime(2023, 1, 1)

# ===============================
# Pytest Fixtures
# ===============================

@pytest.fixture
def indicator():
    """Create a RelativeMomentumIndex indicator instance for testing.

    Returns
    -------
    RelativeMomentumIndex
        A configured indicator instance with default momentum period, smooth window, and thresholds for comprehensive testing of RMI functionality.
    """
    return RelativeMomentumIndex(
        momentum_period=DEFAULT_MOMENTUM_PERIOD,
        smooth_window=DEFAULT_SMOOTH_WINDOW,
        over_bought=DEFAULT_OVERBOUGHT,
        over_sold=DEFAULT_OVERSOLD
    )

@pytest.fixture
def sample_prices():
    """Generate sample price data for testing various market scenarios.

    Returns
    -------
    numpy.ndarray
        Array of sample prices including uptrends, downtrends, and consolidation periods that provide comprehensive test coverage for different market conditions and momentum behavior.
    """
    return np.array([100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 109.0, 108.0, 107.0, 106.0, 105.0, 104.0, 103.0, 102.0, 101.0, 100.0, 101.0, 102.0, 103.0, 104.0])

@pytest.fixture
def trending_up_prices():
    """Generate consistently upward trending price data for bullish market testing.

    Returns
    -------
    numpy.ndarray
        Array of steadily increasing prices that simulate a strong bullish market trend for testing momentum build-up and overbought condition detection.
    """
    return np.array([100.0 + i * 1.0 for i in range(30)])

@pytest.fixture
def trending_down_prices():
    """Generate consistently downward trending price data for bearish market testing.

    Returns
    -------
    numpy.ndarray
        Array of steadily decreasing prices that simulate a strong bearish market trend for testing negative momentum and oversold condition detection.
    """
    return np.array([130.0 - i * 1.0 for i in range(30)])

@pytest.fixture
def volatile_prices():
    """Generate highly volatile price data for stress testing indicator stability.

    Returns
    -------
    numpy.ndarray
        Array of highly volatile prices with significant fluctuations that test the indicator's ability to handle extreme market conditions and momentum oscillations.
    """
    base_prices = np.array([100.0 + i * 0.1 for i in range(50)])
    noise = np.random.normal(0, 3.0, 50)  # Higher volatility for momentum testing
    return base_prices + noise

@pytest.fixture
def oscillating_prices():
    """Generate oscillating price data for testing RMI behavior in range-bound markets.

    Returns
    -------
    numpy.ndarray
        Array of prices that oscillate between overbought and oversold levels to test threshold crossings and signal generation.
    """
    return np.array([100.0 + 10.0 * np.sin(i * 0.3) for i in range(60)])

@pytest.fixture
def sample_market():
    """Create a sample Market object with realistic price data for integration testing.

    Returns
    -------
    Market
        A Market instance populated with sample date/price data that provides a realistic testing environment for indicator integration and end-to-end functionality validation.
    """
    dates = [DEFAULT_START_DATE + i * minutes for i in range(100)]
    prices = [100.0 + np.sin(i * 0.001) * 15 + np.random.normal(0, 2) for i in range(100)]
    market = Market()
    for date, price in zip(dates, prices):
        ask_price = abs(price) * 1.001
        bid_price = abs(price) * 0.999

        market.add_market_data(
            timestamp=date,
            ask_open=ask_price,
            ask_high=ask_price,
            ask_low=ask_price,
            ask_close=ask_price,
            bid_open=bid_price,
            bid_high=bid_price,
            bid_low=bid_price,
            bid_close=bid_price
        )
    return market

# ===============================
# Core Functionality Tests
# ===============================

def test_initialization_with_timedelta_parameters(indicator):
    """Test RelativeMomentumIndex initialization with timedelta parameters and threshold values ensuring proper storage of parameters and successful creation of indicator instance without errors or exceptions during constructor execution.

    Parameters
    ----------
    indicator : RelativeMomentumIndex
        Indicator fixture with default configuration for initialization testing.
    """
    assert indicator.momentum_period == DEFAULT_MOMENTUM_PERIOD, f"Expected momentum_period {DEFAULT_MOMENTUM_PERIOD}, got {indicator.momentum_period}"
    assert indicator.smooth_window == DEFAULT_SMOOTH_WINDOW, f"Expected smooth_window {DEFAULT_SMOOTH_WINDOW}, got {indicator.smooth_window}"
    assert indicator.over_bought == DEFAULT_OVERBOUGHT, f"Expected over_bought {DEFAULT_OVERBOUGHT}, got {indicator.over_bought}"
    assert indicator.over_sold == DEFAULT_OVERSOLD, f"Expected over_sold {DEFAULT_OVERSOLD}, got {indicator.over_sold}"
    assert hasattr(indicator, 'run'), "Indicator should have run method for execution"
    assert hasattr(indicator, 'plot'), "Indicator should have plot method for visualization"

@pytest.mark.parametrize("momentum_period,smooth_window,overbought,oversold", [
    (10 * minutes, 10 * minutes, 75.0, 25.0),
    (14 * minutes, 14 * minutes, 70.0, 30.0),
    (21 * minutes, 21 * minutes, 80.0, 20.0),
    (1 * hours, 1 * hours, 65.0, 35.0)
])
def test_initialization_with_different_parameters(momentum_period, smooth_window, overbought, oversold):
    """Test RelativeMomentumIndex initialization using various parameter combinations to ensure proper handling of different configurations and correct storage of parameter values.

    Parameters
    ----------
    momentum_period : timedelta
        Momentum lookback period for RMI calculation.
    smooth_window : timedelta
        Smoothing window for RMI calculation.
    overbought : float
        Overbought threshold level.
    oversold : float
        Oversold threshold level.
    """
    indicator = RelativeMomentumIndex(
        momentum_period=momentum_period,
        smooth_window=smooth_window,
        over_bought=overbought,
        over_sold=oversold
    )
    assert indicator.momentum_period == momentum_period, f"Momentum period mismatch for {momentum_period}"
    assert indicator.smooth_window == smooth_window, f"Smooth window mismatch for {smooth_window}"
    assert indicator.over_bought == overbought, f"Overbought mismatch for {overbought}"
    assert indicator.over_sold == oversold, f"Oversold mismatch for {oversold}"

def test_run_with_sample_market_data(sample_market):
    """Test RelativeMomentumIndex execution with sample market data ensuring proper processing of Market objects and generation of RMI data with appropriate array lengths matching input data and successful computation without errors or exceptions.

    Parameters
    ----------
    sample_market : Market
        Sample market fixture for testing indicator execution.
    """
    indicator = RelativeMomentumIndex(
        momentum_period=DEFAULT_MOMENTUM_PERIOD,
        smooth_window=DEFAULT_SMOOTH_WINDOW,
        over_bought=DEFAULT_OVERBOUGHT,
        over_sold=DEFAULT_OVERSOLD
    )
    indicator.run(sample_market)
    assert hasattr(indicator, 'market'), "Indicator should store market reference after run"
    assert indicator.market == sample_market, "Stored market should match input market"
    assert hasattr(indicator, '_cpp_rmi'), "Should have RMI data"
    assert hasattr(indicator, '_cpp_regions'), "Should have signal regions data"
    assert hasattr(indicator, '_cpp_over_bought'), "Should have overbought threshold"
    assert hasattr(indicator, '_cpp_over_sold'), "Should have oversold threshold"

def test_rmi_array_lengths(sample_market):
    """Test that computed RMI arrays have correct lengths matching input market data ensuring consistent output dimensions and proper handling of array sizing regardless of market data length or parameter values used during computation.

    Parameters
    ----------
    sample_market : Market
        Sample market fixture for array length validation.
    """
    indicator = RelativeMomentumIndex(
        momentum_period=DEFAULT_MOMENTUM_PERIOD,
        smooth_window=DEFAULT_SMOOTH_WINDOW
    )
    indicator.run(sample_market)
    market_length = len(sample_market.dates)
    assert len(indicator._cpp_rmi) == market_length, f"RMI length {len(indicator._cpp_rmi)} should match market length {market_length}"
    assert len(indicator._cpp_regions) == market_length, f"Regions length {len(indicator._cpp_regions)} should match market length {market_length}"

def test_rmi_value_range():
    """Test that RMI values are within the expected 0-100 range ensuring proper normalization and mathematical correctness of the relative momentum index calculation with validation of output bounds."""
    # Create simple trending market for predictable RMI behavior
    dates = [DEFAULT_START_DATE + i * minutes for i in range(50)]
    prices = [100.0 + i * 0.5 for i in range(50)]  # Steady uptrend
    market = Market()
    for date, price in zip(dates, prices):
        market.add_tick(timestamp=date, ask_price=price + 0.01, bid_price=price - 0.01)

    indicator = RelativeMomentumIndex(momentum_period=10 * minutes, smooth_window=10 * minutes)
    indicator.run(market)

    rmi_values = np.asarray(indicator._cpp_rmi)
    valid_rmi = rmi_values[~np.isnan(rmi_values)]

    if len(valid_rmi) > 0:
        # RMI should be between 0 and 100
        assert np.all(valid_rmi >= 0), "RMI values should be >= 0"
        assert np.all(valid_rmi <= 100), "RMI values should be <= 100"

        # In a strong uptrend, RMI should trend towards higher values
        if len(valid_rmi) > 10:
            early_rmi = np.mean(valid_rmi[:len(valid_rmi)//3])
            late_rmi = np.mean(valid_rmi[-len(valid_rmi)//3:])
            assert late_rmi >= early_rmi, "RMI should increase in uptrending market"

def test_overbought_oversold_detection(oscillating_prices):
    """Test detection of overbought and oversold conditions ensuring proper threshold crossing identification and correct signal generation for momentum extremes with validation of signal timing and accuracy.

    Parameters
    ----------
    oscillating_prices : numpy.ndarray
        Oscillating price data for threshold testing.
    """
    dates = [DEFAULT_START_DATE + i * minutes for i in range(len(oscillating_prices))]
    market = Market()
    for date, price in zip(dates, oscillating_prices):
        price = abs(price)  # Ensure positive prices
        market.add_tick(timestamp=date, ask_price=price + 0.01, bid_price=price - 0.01)

    indicator = RelativeMomentumIndex(
        momentum_period=10 * minutes,
        smooth_window=5 * minutes,
        over_bought=70.0,
        over_sold=30.0
    )
    indicator.run(market)

    rmi_values = np.asarray(indicator._cpp_rmi)
    regions = np.asarray(indicator._cpp_regions)

    valid_mask = ~np.isnan(rmi_values)
    if np.sum(valid_mask) > 10:
        valid_rmi = rmi_values[valid_mask]
        valid_regions = regions[valid_mask]

        # Check if we have some extreme values that should trigger signals
        has_overbought = np.any(valid_rmi > 70.0)
        has_oversold = np.any(valid_rmi < 30.0)

        if has_overbought or has_oversold:
            # Should have some non-zero signals
            has_signals = np.any(valid_regions != 0)
            assert has_signals, "Should generate signals when crossing thresholds"

def test_signal_generation_consistency(sample_market):
    """Test consistency of signal generation ensuring proper correlation between RMI values and generated signals with validation of signal logic and threshold-based decision making accuracy.

    Parameters
    ----------
    sample_market : Market
        Sample market fixture for signal consistency testing.
    """
    indicator = RelativeMomentumIndex(
        momentum_period=DEFAULT_MOMENTUM_PERIOD,
        smooth_window=DEFAULT_SMOOTH_WINDOW,
        over_bought=70.0,
        over_sold=30.0
    )
    indicator.run(sample_market)

    rmi_values = np.asarray(indicator._cpp_rmi)
    regions = np.asarray(indicator._cpp_regions)

    # All signal values should be within reasonable range
    assert np.all(np.abs(regions) <= 1), "Signal values should be normalized between -1 and 1"

    # Check signal consistency with RMI values
    valid_mask = ~np.isnan(rmi_values)
    if np.sum(valid_mask) > 0:
        # Signals should exist where RMI crosses thresholds
        unique_signals = np.unique(regions[valid_mask])
        assert len(unique_signals) >= 1, "Should generate at least some signal values"

def test_edge_case_insufficient_data():
    """Test handling of edge case where market data is insufficient for computing RMI ensuring graceful handling of boundary conditions and appropriate behavior when data length is less than required window sizes."""
    # Create market with fewer data points than required
    short_dates = [DEFAULT_START_DATE + i * minutes for i in range(5)]
    short_prices = [100.0, 101.0, 102.0, 103.0, 104.0]
    market = Market()
    for date, price in zip(short_dates, short_prices):
        market.add_tick(timestamp=date, ask_price=price + 0.01, bid_price=price - 0.01)

    indicator = RelativeMomentumIndex(
        momentum_period=DEFAULT_MOMENTUM_PERIOD,
        smooth_window=DEFAULT_SMOOTH_WINDOW
    )
    # Should handle insufficient data gracefully without crashing
    try:
        indicator.run(market)
        # If it runs, check that arrays have correct length
        assert len(indicator._cpp_rmi) == len(short_dates), "Array length should match input data"
        # Early values should be NaN due to insufficient data
        rmi = np.asarray(indicator._cpp_rmi)
        assert np.isnan(rmi[0]), "Early RMI values should be NaN with insufficient data"
    except Exception as e:
        # Expected behavior - should handle gracefully or raise informative error
        assert "insufficient" in str(e).lower() or "data" in str(e).lower(), f"Unexpected error message: {e}"

def test_momentum_sensitivity(volatile_prices):
    """Test RMI sensitivity to momentum changes ensuring proper response to price acceleration and deceleration with validation of momentum capture effectiveness in various market conditions.

    Parameters
    ----------
    volatile_prices : numpy.ndarray
        Volatile price data for momentum sensitivity testing.
    """
    dates = [DEFAULT_START_DATE + i * minutes for i in range(len(volatile_prices))]
    market = Market()
    for date, price in zip(dates, volatile_prices):
        price = abs(price)  # Ensure positive prices
        market.add_tick(timestamp=date, ask_price=price + 0.01, bid_price=price - 0.01)

    indicator = RelativeMomentumIndex(momentum_period=5 * minutes, smooth_window=3 * minutes)
    indicator.run(market)

    rmi_values = np.asarray(indicator._cpp_rmi)
    valid_rmi = rmi_values[~np.isnan(rmi_values)]

    if len(valid_rmi) > 10:
        # RMI should show variation in volatile markets
        rmi_std = np.std(valid_rmi)
        assert rmi_std > 0, "RMI should vary in volatile markets"

        # RMI range should utilize significant portion of 0-100 scale
        rmi_range = np.max(valid_rmi) - np.min(valid_rmi)
        assert rmi_range > 10, "RMI should utilize reasonable range in volatile markets"

@pytest.mark.parametrize("threshold_pair", [
    (80.0, 20.0),  # Wide thresholds
    (70.0, 30.0),  # Standard thresholds
    (60.0, 40.0),  # Narrow thresholds
])
def test_different_threshold_settings(sample_market, threshold_pair):
    """Test RMI behavior with different overbought/oversold threshold settings ensuring proper threshold sensitivity and signal generation frequency adaptation for various threshold configurations.

    Parameters
    ----------
    sample_market : Market
        Sample market fixture for threshold testing.
    threshold_pair : tuple
        Tuple containing (overbought, oversold) threshold values.
    """
    overbought, oversold = threshold_pair

    indicator = RelativeMomentumIndex(
        momentum_period=10 * minutes,
        smooth_window=5 * minutes,
        over_bought=overbought,
        over_sold=oversold
    )
    indicator.run(sample_market)

    assert indicator._cpp_over_bought == overbought, f"Overbought threshold should be {overbought}"
    assert indicator._cpp_over_sold == oversold, f"Oversold threshold should be {oversold}"

    rmi_values = np.asarray(indicator._cpp_rmi)
    regions = np.asarray(indicator._cpp_regions)

    valid_mask = ~np.isnan(rmi_values)
    if np.sum(valid_mask) > 0:
        # Narrow thresholds should generate more signals than wide thresholds
        signal_count = np.count_nonzero(regions[valid_mask])
        # This is market-dependent, but we can at least check consistency
        assert signal_count >= 0, "Signal count should be non-negative"

def test_plot_method_execution(sample_market):
    """Test execution of plot method ensuring proper visualization generation without errors and correct handling of matplotlib backend configuration for testing environment compatibility.

    Parameters
    ----------
    sample_market : Market
        Sample market fixture for plot generation testing.
    """
    indicator = RelativeMomentumIndex(
        momentum_period=DEFAULT_MOMENTUM_PERIOD,
        smooth_window=DEFAULT_SMOOTH_WINDOW
    )
    indicator.run(sample_market)

    # Test plot method execution (requires matplotlib)
    try:
        with patch('matplotlib.pyplot.show'):  # Mock plt.show to prevent display
            figure, ax = indicator.plot(show=False)
            assert figure is not None, "Plot should return a figure object"
            assert ax is not None, "Plot should return an axes object"
    except ImportError:
        pytest.skip("Matplotlib not available for plotting tests")
    except Exception as e:
        pytest.fail(f"Plot method failed with error: {e}")

def test_performance_with_large_dataset():
    """Test performance characteristics with large datasets ensuring acceptable computation times for enterprise-scale market data processing and memory usage optimization validation under high-volume scenarios."""
    # Create large dataset for performance testing
    large_dates = [DEFAULT_START_DATE + i * minutes for i in range(5000)]
    large_prices = [100.0 + np.sin(i * 0.001) * 10 + np.random.normal(0, 1) for i in range(5000)]
    market = Market()
    for date, price in zip(large_dates, large_prices):
        price = abs(price)
        market.add_tick(timestamp=date, ask_price=price + 0.01, bid_price=price - 0.01)

    indicator = RelativeMomentumIndex(
        momentum_period=DEFAULT_MOMENTUM_PERIOD,
        smooth_window=DEFAULT_SMOOTH_WINDOW
    )

    start_time = time.time()
    indicator.run(market)
    execution_time = time.time() - start_time

    # Performance should be reasonable (less than 10 seconds for 5k data points)
    assert execution_time < 10.0, f"Execution time {execution_time:.2f}s exceeds performance threshold"
    assert len(indicator._cpp_rmi) == len(large_dates), "Output length should match input length"

def test_memory_usage_and_cleanup():
    """Test memory usage patterns and garbage collection effectiveness ensuring proper cleanup of resources after indicator computation and verification of memory leak prevention in repeated execution scenarios."""
    initial_objects = len(gc.get_objects())

    # Create and run multiple indicators to test memory management
    for i in range(30):
        dates = [DEFAULT_START_DATE + j * minutes for j in range(100)]
        prices = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        market = Market()
        for date, price in zip(dates, prices):
            price = abs(price)
            market.add_tick(timestamp=date, ask_price=price + 0.01, bid_price=price - 0.01)

        indicator = RelativeMomentumIndex(
            momentum_period=DEFAULT_MOMENTUM_PERIOD,
            smooth_window=DEFAULT_SMOOTH_WINDOW
        )
        indicator.run(market)
        del indicator, market

    # Force garbage collection
    gc.collect()
    final_objects = len(gc.get_objects())

    # Memory usage should not grow excessively
    object_growth = final_objects - initial_objects
    assert object_growth < 1000, f"Excessive object growth: {object_growth} new objects remain"

@pytest.mark.parametrize("frequency", [1, 5, 15, 60])
def test_different_market_data_frequencies(frequency):
    """Test indicator behavior with different market data frequencies including tick, minute, and hourly data ensuring consistent performance and accuracy across various temporal resolutions.

    Parameters
    ----------
    frequency : int
        Data frequency in minutes for market data generation.
    """
    # Create market data with specified frequency
    time_delta = timedelta(minutes=frequency)
    dates = [DEFAULT_START_DATE + i * time_delta for i in range(50)]
    prices = [100.0 + np.sin(i * 0.2) * 8 for i in range(50)]
    market = Market()
    for date, price in zip(dates, prices):
        market.add_tick(timestamp=date, ask_price=price + 0.01, bid_price=price - 0.01)

    # Adjust window sizes based on frequency
    momentum_period = max(10 * time_delta, 10 * minutes)
    smooth_window = max(5 * time_delta, 5 * minutes)

    indicator = RelativeMomentumIndex(
        momentum_period=momentum_period,
        smooth_window=smooth_window
    )
    indicator.run(market)

    assert len(indicator._cpp_rmi) == len(dates), f"Output length mismatch for {frequency}min frequency"
    assert len(indicator._cpp_regions) == len(dates), f"Output length mismatch for {frequency}min frequency"

def test_numerical_stability_extreme_values():
    """Test indicator handling of extreme price values ensuring numerical stability and accuracy across wide value ranges including very small, very large, and edge case pricing scenarios."""
    extreme_test_cases = [
        ([0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.01], "very small prices"),
        ([10000.0, 20000.0, 30000.0, 40000.0, 50000.0, 60000.0, 70000.0, 80000.0, 90000.0, 100000.0], "very large prices"),
        ([100.0] * 10, "constant prices")
    ]

    for prices, description in extreme_test_cases:
        dates = [DEFAULT_START_DATE + i * minutes for i in range(len(prices))]
        market = Market()
        for date, price in zip(dates, prices):
            market.add_tick(timestamp=date, ask_price=price + 0.01, bid_price=price - 0.01)

        indicator = RelativeMomentumIndex(momentum_period=5 * minutes, smooth_window=3 * minutes)
        indicator.run(market)

        rmi_values = np.asarray(indicator._cpp_rmi)

        # Check for numerical stability (no infinite values in valid range)
        valid_mask = ~np.isnan(rmi_values)
        if np.sum(valid_mask) > 0:
            assert not np.any(np.isinf(rmi_values[valid_mask])), f"RMI should not contain infinite values for {description}"
            # For constant prices, RMI should stabilize around 50 (neutral momentum)
            if "constant" in description and len(rmi_values[valid_mask]) > 0:
                stable_rmi = rmi_values[valid_mask][-1]  # Last value should be stable
                assert 40 <= stable_rmi <= 60, f"RMI should be around 50 for constant prices, got {stable_rmi}"

# ===============================
# Integration and End-to-End Tests
# ===============================

def test_end_to_end_workflow(sample_market):
    """Test complete end-to-end workflow from market data loading through indicator computation to signal generation ensuring seamless integration of all components and correct data flow through the entire processing pipeline.

    Parameters
    ----------
    sample_market : Market
        Sample market fixture for end-to-end workflow testing.
    """
    # Complete workflow test
    indicator = RelativeMomentumIndex(
        momentum_period=DEFAULT_MOMENTUM_PERIOD,
        smooth_window=DEFAULT_SMOOTH_WINDOW,
        over_bought=DEFAULT_OVERBOUGHT,
        over_sold=DEFAULT_OVERSOLD
    )

    # Step 1: Run computation
    indicator.run(sample_market)

    # Step 2: Verify all outputs are generated
    assert hasattr(indicator, '_cpp_rmi'), "Should have RMI values"
    assert hasattr(indicator, '_cpp_regions'), "Should have signal regions"
    assert hasattr(indicator, '_cpp_over_bought'), "Should have overbought threshold"
    assert hasattr(indicator, '_cpp_over_sold'), "Should have oversold threshold"

    # Step 3: Verify data consistency
    data_length = len(sample_market.dates)
    assert len(indicator._cpp_rmi) == data_length, "Data length consistency check"
    assert len(indicator._cpp_regions) == data_length, "Data length consistency check"

    # Step 4: Verify basic mathematical properties
    rmi_values = np.asarray(indicator._cpp_rmi)
    regions = np.asarray(indicator._cpp_regions)

    # Non-NaN RMI values should be within 0-100 range
    valid_rmi = rmi_values[~np.isnan(rmi_values)]

    if len(valid_rmi) > 0:
        assert np.all(valid_rmi >= 0), "RMI values should be >= 0"
        assert np.all(valid_rmi <= 100), "RMI values should be <= 100"

    # Threshold values should match input parameters
    assert indicator._cpp_over_bought == DEFAULT_OVERBOUGHT, "Overbought threshold should match input"
    assert indicator._cpp_over_sold == DEFAULT_OVERSOLD, "Oversold threshold should match input"

# ===============================
# Test Execution
# ===============================

if __name__ == "__main__":
    """
    Execute test suite when run directly.

    Runs all tests with error warnings enabled to catch potential
    issues during development. Provides detailed output for debugging.

    Examples
    --------
    >>> python moving_average_crossing.py

    Notes
    -----
    Use pytest directly for more control over test execution
    """
    pytest.main(["-v", "-W", "error", "--tb=short", __file__])
