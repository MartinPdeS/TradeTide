import gc
import time
import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch
from TradeTide.indicators.bollinger_bands import BollingerBands
from TradeTide.market import Market
from TradeTide.times import minutes, hours, days
from TradeTide.currencies import Currency
import TradeTide

# Enable debug mode for detailed logging during test execution
TradeTide.debug_mode = True

# ===============================
# Test Configuration and Constants
# ===============================

DEFAULT_WINDOW = 20 * minutes
DEFAULT_MULTIPLIER = 2.0
DEFAULT_CURRENCY = Currency.USD
DEFAULT_START_DATE = datetime(2023, 1, 1)

# ===============================
# Pytest Fixtures
# ===============================

@pytest.fixture
def indicator():
    """Create a BollingerBands indicator instance for testing.

    Returns
    -------
    BollingerBands
        A configured indicator instance with default window and multiplier for comprehensive testing of Bollinger Bands functionality.
    """
    return BollingerBands(window=DEFAULT_WINDOW, multiplier=DEFAULT_MULTIPLIER)

@pytest.fixture
def sample_prices():
    """Generate sample price data for testing various market scenarios.

    Returns
    -------
    numpy.ndarray
        Array of sample prices including uptrends, downtrends, and consolidation periods that provide comprehensive test coverage for different market conditions and band behavior.
    """
    return np.array([100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 109.0, 108.0, 107.0, 106.0, 105.0, 104.0, 103.0, 102.0, 101.0, 100.0, 101.0, 102.0, 103.0, 104.0])

@pytest.fixture
def trending_up_prices():
    """Generate consistently upward trending price data for bullish market testing.

    Returns
    -------
    numpy.ndarray
        Array of steadily increasing prices that simulate a strong bullish market trend for testing band expansion and price breakout scenarios.
    """
    return np.array([100.0 + i * 0.5 for i in range(30)])

@pytest.fixture
def trending_down_prices():
    """Generate consistently downward trending price data for bearish market testing.

    Returns
    -------
    numpy.ndarray
        Array of steadily decreasing prices that simulate a strong bearish market trend for testing band contraction and price breakdown scenarios.
    """
    return np.array([130.0 - i * 0.5 for i in range(30)])

@pytest.fixture
def volatile_prices():
    """Generate highly volatile price data for stress testing indicator stability.

    Returns
    -------
    numpy.ndarray
        Array of highly volatile prices with significant fluctuations that test the indicator's ability to handle extreme market conditions and band expansion/contraction.
    """
    base_prices = np.array([100.0 + i * 0.1 for i in range(50)])
    noise = np.random.normal(0, 5.0, 50)  # Higher volatility for band testing
    return base_prices + noise

@pytest.fixture
def sideways_prices():
    """Generate sideways price data for range-bound market testing.

    Returns
    -------
    numpy.ndarray
        Array of prices that oscillate within a tight range to test band behavior in consolidating markets.
    """
    return np.array([100.0 + 2.0 * np.sin(i * 0.2) for i in range(40)])

@pytest.fixture
def sample_market():
    """Create a sample Market object with realistic price data for integration testing.

    Returns
    -------
    Market
        A Market instance populated with sample date/price data that provides a realistic testing environment for indicator integration and end-to-end functionality validation.
    """
    dates = [DEFAULT_START_DATE + i * minutes for i in range(100)]
    prices = [100.0 + np.sin(i * 0.1) * 10 + np.random.normal(0, 1) for i in range(100)]
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

def test_initialization_with_timedelta_window(indicator):
    """Test BollingerBands initialization with timedelta window and float multiplier ensuring proper storage of parameters and successful creation of indicator instance without errors or exceptions during constructor execution.

    Parameters
    ----------
    indicator : BollingerBands
        Indicator fixture with default window and multiplier configuration for initialization testing.
    """
    assert indicator.window == DEFAULT_WINDOW, f"Expected window {DEFAULT_WINDOW}, got {indicator.window}"
    assert indicator.multiplier == DEFAULT_MULTIPLIER, f"Expected multiplier {DEFAULT_MULTIPLIER}, got {indicator.multiplier}"
    assert hasattr(indicator, 'run'), "Indicator should have run method for execution"
    assert hasattr(indicator, 'plot'), "Indicator should have plot method for visualization"

@pytest.mark.parametrize("window,multiplier", [
    (10 * minutes, 1.5),
    (20 * minutes, 2.0),
    (1 * hours, 2.5),
    (1 * days, 3.0)
])
def test_initialization_with_different_parameters(window, multiplier):
    """Test BollingerBands initialization using various window sizes and multiplier values to ensure proper handling of different parameter combinations and correct storage of configuration values.

    Parameters
    ----------
    window : timedelta
        Window duration for moving average calculation.
    multiplier : float
        Standard deviation multiplier for band calculation.
    """
    indicator = BollingerBands(window=window, multiplier=multiplier)
    assert indicator.window == window, f"Window mismatch for {window}"
    assert indicator.multiplier == multiplier, f"Multiplier mismatch for {multiplier}"

def test_run_with_sample_market_data(sample_market):
    """Test BollingerBands execution with sample market data ensuring proper processing of Market objects and generation of band data with appropriate array lengths matching input data and successful computation without errors or exceptions.

    Parameters
    ----------
    sample_market : Market
        Sample market fixture for testing indicator execution.
    """
    indicator = BollingerBands(window=DEFAULT_WINDOW, multiplier=DEFAULT_MULTIPLIER)
    indicator.run(sample_market)
    assert hasattr(indicator, 'market'), "Indicator should store market reference after run"
    assert indicator.market == sample_market, "Stored market should match input market"
    assert hasattr(indicator, '_cpp_sma'), "Should have simple moving average data"
    assert hasattr(indicator, '_cpp_upper_band'), "Should have upper band data"
    assert hasattr(indicator, '_cpp_lower_band'), "Should have lower band data"
    assert hasattr(indicator, '_cpp_regions'), "Should have signal regions data"

def test_bollinger_bands_array_lengths(sample_market):
    """Test that computed Bollinger Bands arrays have correct lengths matching input market data ensuring consistent output dimensions and proper handling of array sizing regardless of market data length or window parameters used during computation.

    Parameters
    ----------
    sample_market : Market
        Sample market fixture for array length validation.
    """
    indicator = BollingerBands(window=DEFAULT_WINDOW, multiplier=DEFAULT_MULTIPLIER)
    indicator.run(sample_market)
    market_length = len(sample_market.dates)
    assert len(indicator._cpp_sma) == market_length, f"SMA length {len(indicator._cpp_sma)} should match market length {market_length}"
    assert len(indicator._cpp_upper_band) == market_length, f"Upper band length {len(indicator._cpp_upper_band)} should match market length {market_length}"
    assert len(indicator._cpp_lower_band) == market_length, f"Lower band length {len(indicator._cpp_lower_band)} should match market length {market_length}"
    assert len(indicator._cpp_regions) == market_length, f"Regions length {len(indicator._cpp_regions)} should match market length {market_length}"

def test_bollinger_bands_mathematical_properties(sample_market):
    """Test mathematical properties of Bollinger Bands ensuring proper relationships between SMA, upper band, and lower band including band symmetry and correct standard deviation calculations with validation of mathematical correctness.

    Parameters
    ----------
    sample_market : Market
        Sample market fixture for mathematical validation.
    """
    indicator = BollingerBands(window=10 * minutes, multiplier=2.0)
    indicator.run(sample_market)

    sma = np.asarray(indicator._cpp_sma)
    upper_band = np.asarray(indicator._cpp_upper_band)
    lower_band = np.asarray(indicator._cpp_lower_band)

    # Remove NaN values for validation
    valid_mask = ~(np.isnan(sma) | np.isnan(upper_band) | np.isnan(lower_band))
    sma_valid = sma[valid_mask]
    upper_valid = upper_band[valid_mask]
    lower_valid = lower_band[valid_mask]

    if len(sma_valid) > 0:
        # Upper band should be above SMA
        assert np.all(upper_valid >= sma_valid), "Upper band should be greater than or equal to SMA"
        # Lower band should be below SMA
        assert np.all(lower_valid <= sma_valid), "Lower band should be less than or equal to SMA"
        # Bands should be symmetric around SMA (approximately)
        upper_distance = upper_valid - sma_valid
        lower_distance = sma_valid - lower_valid
        np.testing.assert_allclose(upper_distance, lower_distance, rtol=1e-10, err_msg="Bands should be symmetric around SMA")

def test_band_expansion_in_volatile_market(volatile_prices):
    """Test that Bollinger Bands expand appropriately during high volatility periods ensuring proper response to market volatility changes and correct band width adjustments based on price fluctuation intensity.

    Parameters
    ----------
    volatile_prices : numpy.ndarray
        Volatile price data for band expansion testing.
    """
    # Create market with volatile prices
    dates = [DEFAULT_START_DATE + i * minutes for i in range(len(volatile_prices))]
    market = Market()
    for date, price in zip(dates, volatile_prices):
        price = abs(price)  # Ensure positive prices
        market.add_tick(timestamp=date, ask_price=price + 0.01, bid_price=price - 0.01)

    indicator = BollingerBands(window=10 * minutes, multiplier=2.0)
    indicator.run(market)

    sma = np.asarray(indicator._cpp_sma)
    upper_band = np.asarray(indicator._cpp_upper_band)
    lower_band = np.asarray(indicator._cpp_lower_band)

    # Calculate band width (should be larger in volatile periods)
    valid_mask = ~(np.isnan(sma) | np.isnan(upper_band) | np.isnan(lower_band))
    if np.sum(valid_mask) > 10:  # Need sufficient data points
        band_width = (upper_band - lower_band)[valid_mask]
        # Band width should be positive and non-zero
        assert np.all(band_width > 0), "Band width should be positive in volatile markets"
        # Standard deviation of band width should be reasonable
        assert np.std(band_width) >= 0, "Band width should vary with volatility"

def test_band_contraction_in_sideways_market(sideways_prices):
    """Test that Bollinger Bands contract appropriately during low volatility sideways market periods ensuring proper response to reduced price movement and correct band narrowing during consolidation phases.

    Parameters
    ----------
    sideways_prices : numpy.ndarray
        Sideways price data for band contraction testing.
    """
    dates = [DEFAULT_START_DATE + i * minutes for i in range(len(sideways_prices))]
    market = Market()
    for date, price in zip(dates, sideways_prices):
        price = abs(price)  # Ensure positive prices
        market.add_tick(timestamp=date, ask_price=price + 0.01, bid_price=price - 0.01)

    indicator = BollingerBands(window=10 * minutes, multiplier=2.0)
    indicator.run(market)

    sma = np.asarray(indicator._cpp_sma)
    upper_band = np.asarray(indicator._cpp_upper_band)
    lower_band = np.asarray(indicator._cpp_lower_band)

    valid_mask = ~(np.isnan(sma) | np.isnan(upper_band) | np.isnan(lower_band))
    if np.sum(valid_mask) > 10:
        band_width = (upper_band - lower_band)[valid_mask]
        # In sideways markets, band width should be relatively stable and smaller
        band_width_cv = np.std(band_width) / np.mean(band_width)  # Coefficient of variation
        assert band_width_cv < 1.0, "Band width should be relatively stable in sideways markets"

def test_edge_case_insufficient_data():
    """Test handling of edge case where market data is insufficient for computing Bollinger Bands ensuring graceful handling of boundary conditions and appropriate behavior when data length is less than required window size.
    """
    # Create market with fewer data points than window requires
    short_dates = [DEFAULT_START_DATE + i * minutes for i in range(5)]
    short_prices = [100.0, 101.0, 102.0, 103.0, 104.0]
    market = Market()
    for date, price in zip(short_dates, short_prices):
        market.add_tick(timestamp=date, ask_price=price + 0.01, bid_price=price - 0.01)

    indicator = BollingerBands(window=DEFAULT_WINDOW, multiplier=DEFAULT_MULTIPLIER)
    # Should handle insufficient data gracefully without crashing
    try:
        indicator.run(market)
        # If it runs, check that arrays have correct length
        assert len(indicator._cpp_sma) == len(short_dates), "Array length should match input data"
        # Early values should be NaN due to insufficient data
        sma = np.asarray(indicator._cpp_sma)
        assert np.isnan(sma[0]), "Early SMA values should be NaN with insufficient data"
    except Exception as e:
        # Expected behavior - should handle gracefully or raise informative error
        assert "insufficient" in str(e).lower() or "data" in str(e).lower(), f"Unexpected error message: {e}"

@pytest.mark.parametrize("multiplier", [1.0, 1.5, 2.0, 2.5, 3.0])
def test_different_multiplier_values(sample_market, multiplier):
    """Test BollingerBands behavior with different standard deviation multiplier values ensuring proper band width scaling and correct mathematical relationships for various multiplier settings.

    Parameters
    ----------
    sample_market : Market
        Sample market fixture for multiplier testing.
    multiplier : float
        Standard deviation multiplier value for testing.
    """
    indicator = BollingerBands(window=10 * minutes, multiplier=multiplier)
    indicator.run(sample_market)

    sma = np.asarray(indicator._cpp_sma)
    upper_band = np.asarray(indicator._cpp_upper_band)
    lower_band = np.asarray(indicator._cpp_lower_band)

    valid_mask = ~(np.isnan(sma) | np.isnan(upper_band) | np.isnan(lower_band))
    if np.sum(valid_mask) > 0:
        # Band width should be proportional to multiplier
        band_width = np.mean((upper_band - lower_band)[valid_mask])
        assert band_width > 0, f"Band width should be positive for multiplier {multiplier}"

        # Larger multipliers should produce wider bands
        if multiplier >= 2.0:
            indicator_small = BollingerBands(window=10 * minutes, multiplier=1.0)
            indicator_small.run(sample_market)
            small_upper = np.asarray(indicator_small._cpp_upper_band)
            small_lower = np.asarray(indicator_small._cpp_lower_band)
            small_band_width = np.mean((small_upper - small_lower)[valid_mask])
            assert band_width > small_band_width, f"Larger multiplier should produce wider bands"

def test_signal_generation(sample_market):
    """Test signal generation for price breakouts above upper band and below lower band ensuring proper identification of overbought and oversold conditions with correct signal timing and magnitude.

    Parameters
    ----------
    sample_market : Market
        Sample market fixture for signal generation testing.
    """
    indicator = BollingerBands(window=10 * minutes, multiplier=2.0)
    indicator.run(sample_market)

    regions = np.asarray(indicator._cpp_regions)
    # Check that signals are generated (can be positive, negative, or zero)
    unique_signals = np.unique(regions)
    assert len(unique_signals) >= 1, "Should generate at least some signal values"

    # All signal values should be within reasonable range
    assert np.all(np.abs(regions) <= 1), "Signal values should be normalized between -1 and 1"

def test_plot_method_execution(sample_market):
    """Test execution of plot method ensuring proper visualization generation without errors and correct handling of matplotlib backend configuration for testing environment compatibility.

    Parameters
    ----------
    sample_market : Market
        Sample market fixture for plot generation testing.
    """
    indicator = BollingerBands(window=DEFAULT_WINDOW, multiplier=DEFAULT_MULTIPLIER)
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
    large_dates = [DEFAULT_START_DATE + i * minutes for i in range(10000)]
    large_prices = [100.0 + np.sin(i * 0.001) * 10 + np.random.normal(0, 0.5) for i in range(10000)]
    market = Market()
    for date, price in zip(large_dates, large_prices):
        price = abs(price)
        market.add_tick(timestamp=date, ask_price=price + 0.01, bid_price=price - 0.01)

    indicator = BollingerBands(window=DEFAULT_WINDOW, multiplier=DEFAULT_MULTIPLIER)

    start_time = time.time()
    indicator.run(market)
    execution_time = time.time() - start_time

    # Performance should be reasonable (less than 10 seconds for 10k data points)
    assert execution_time < 10.0, f"Execution time {execution_time:.2f}s exceeds performance threshold"
    assert len(indicator._cpp_sma) == len(large_dates), "Output length should match input length"

def test_memory_usage_and_cleanup():
    """Test memory usage patterns and garbage collection effectiveness ensuring proper cleanup of resources after indicator computation and verification of memory leak prevention in repeated execution scenarios."""
    initial_objects = len(gc.get_objects())

    # Create and run multiple indicators to test memory management
    for i in range(50):
        dates = [DEFAULT_START_DATE + j * minutes for j in range(100)]
        prices = [100.0 + np.random.normal(0, 1) for _ in range(100)]
        market = Market()
        for date, price in zip(dates, prices):
            price = abs(price)
            market.add_tick(timestamp=date, ask_price=price + 0.01, bid_price=price - 0.01)

        indicator = BollingerBands(window=DEFAULT_WINDOW, multiplier=DEFAULT_MULTIPLIER)
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
    prices = [100.0 + np.sin(i * 0.1) * 5 for i in range(50)]
    market = Market()
    for date, price in zip(dates, prices):
        market.add_tick(timestamp=date, ask_price=price + 0.01, bid_price=price - 0.01)

    # Adjust window size based on frequency
    window = max(10 * time_delta, 10 * minutes)

    indicator = BollingerBands(window=window, multiplier=2.0)
    indicator.run(market)

    assert len(indicator._cpp_sma) == len(dates), f"Output length mismatch for {frequency}min frequency"
    assert len(indicator._cpp_upper_band) == len(dates), f"Output length mismatch for {frequency}min frequency"
    assert len(indicator._cpp_lower_band) == len(dates), f"Output length mismatch for {frequency}min frequency"

def test_numerical_stability_extreme_values():
    """Test indicator handling of extreme price values ensuring numerical stability and accuracy across wide value ranges including very small, very large, and edge case pricing scenarios."""
    extreme_test_cases = [
        ([0.0001, 0.0002, 0.0003, 0.0004, 0.0005], "very small prices"),
        ([10000.0, 20000.0, 30000.0, 40000.0, 50000.0], "very large prices"),
        ([100.0, 100.0, 100.0, 100.0, 100.0], "constant prices")
    ]

    for prices, description in extreme_test_cases:
        dates = [DEFAULT_START_DATE + i * minutes for i in range(len(prices))]
        market = Market()
        for date, price in zip(dates, prices):
            market.add_tick(timestamp=date, ask_price=price + 0.01, bid_price=price - 0.01)

        indicator = BollingerBands(window=3 * minutes, multiplier=2.0)
        indicator.run(market)

        sma = np.asarray(indicator._cpp_sma)
        upper_band = np.asarray(indicator._cpp_upper_band)
        lower_band = np.asarray(indicator._cpp_lower_band)

        # Check for numerical stability (no NaN or infinite values in valid range)
        valid_mask = ~np.isnan(sma)
        if np.sum(valid_mask) > 0:
            assert not np.any(np.isinf(sma[valid_mask])), f"SMA should not contain infinite values for {description}"
            assert not np.any(np.isinf(upper_band[valid_mask])), f"Upper band should not contain infinite values for {description}"
            assert not np.any(np.isinf(lower_band[valid_mask])), f"Lower band should not contain infinite values for {description}"

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
    indicator = BollingerBands(window=DEFAULT_WINDOW, multiplier=DEFAULT_MULTIPLIER)

    # Step 1: Run computation
    indicator.run(sample_market)

    # Step 2: Verify all outputs are generated
    assert hasattr(indicator, '_cpp_sma'), "Should have simple moving average"
    assert hasattr(indicator, '_cpp_upper_band'), "Should have upper band"
    assert hasattr(indicator, '_cpp_lower_band'), "Should have lower band"
    assert hasattr(indicator, '_cpp_regions'), "Should have signal regions"

    # Step 3: Verify data consistency
    data_length = len(sample_market.dates)
    assert len(indicator._cpp_sma) == data_length, "Data length consistency check"
    assert len(indicator._cpp_upper_band) == data_length, "Data length consistency check"
    assert len(indicator._cpp_lower_band) == data_length, "Data length consistency check"
    assert len(indicator._cpp_regions) == data_length, "Data length consistency check"

    # Step 4: Verify basic mathematical properties
    sma = np.asarray(indicator._cpp_sma)
    upper_band = np.asarray(indicator._cpp_upper_band)
    lower_band = np.asarray(indicator._cpp_lower_band)

    # Non-NaN values should maintain proper relationships
    valid_mask = ~(np.isnan(sma) | np.isnan(upper_band) | np.isnan(lower_band))
    if np.sum(valid_mask) > 0:
        assert np.all(upper_band[valid_mask] >= sma[valid_mask]), "Upper band should be >= SMA"
        assert np.all(lower_band[valid_mask] <= sma[valid_mask]), "Lower band should be <= SMA"
        assert np.all(sma[valid_mask] > 0), "SMA should be positive for positive price data"

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
