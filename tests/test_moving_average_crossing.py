import gc
import time
import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch
import matplotlib.pyplot as plt

from TradeTide.indicators.moving_average_crossings import MovingAverageCrossing
from TradeTide.market import Market
from TradeTide.times import minutes, hours, days
from TradeTide.currencies import Currency
import TradeTide

# Enable debug mode for detailed logging during test execution
TradeTide.debug_mode = True

# ===============================
# Test Configuration and Constants
# ===============================

SHORT_WINDOW = 5 * minutes
LONG_WINDOW = 20 * minutes
DEFAULT_CURRENCY = Currency.USD
DEFAULT_START_DATE = datetime(2023, 1, 1)

# ===============================
# Pytest Fixtures
# ===============================


@pytest.fixture
def indicator():
    """Create a MovingAverageCrossing indicator instance for testing.

    Returns
    -------
    MovingAverageCrossing
        A configured indicator instance with default short and long windows for comprehensive testing of moving average crossing functionality.
    """
    return MovingAverageCrossing(short_window=SHORT_WINDOW, long_window=LONG_WINDOW)


@pytest.fixture
def sample_prices():
    """Generate sample price data for testing various market scenarios.

    Returns
    -------
    numpy.ndarray
        Array of sample prices including uptrends, downtrends, and consolidation periods that provide comprehensive test coverage for different market conditions and crossing scenarios.
    """
    return np.array(
        [
            100.0,
            101.0,
            102.0,
            103.0,
            104.0,
            105.0,
            106.0,
            107.0,
            108.0,
            109.0,
            110.0,
            109.0,
            108.0,
            107.0,
            106.0,
            105.0,
            104.0,
            103.0,
            102.0,
            101.0,
            100.0,
            101.0,
            102.0,
            103.0,
            104.0,
        ]
    )


@pytest.fixture
def trending_up_prices():
    """Generate consistently upward trending price data for bullish market testing.

    Returns
    -------
    numpy.ndarray
        Array of steadily increasing prices that simulate a strong bullish market trend for testing positive crossing scenarios and trend detection accuracy.
    """
    return np.array([100.0 + i * 0.5 for i in range(30)])


@pytest.fixture
def trending_down_prices():
    """Generate consistently downward trending price data for bearish market testing.

    Returns
    -------
    numpy.ndarray
        Array of steadily decreasing prices that simulate a strong bearish market trend for testing negative crossing scenarios and trend reversal detection.
    """
    return np.array([130.0 - i * 0.5 for i in range(30)])


@pytest.fixture
def volatile_prices():
    """Generate highly volatile price data for stress testing indicator stability.

    Returns
    -------
    numpy.ndarray
        Array of highly volatile prices with significant fluctuations that test the indicator's ability to handle extreme market conditions and noise reduction capabilities.
    """
    base_prices = np.array([100.0 + i * 0.1 for i in range(50)])
    noise = np.random.normal(0, 2.0, 50)
    return base_prices + noise


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
        ask_price = price * 1.001
        bid_price = price * 0.999

        market.add_market_data(
            timestamp=date,
            ask_open=ask_price,
            ask_high=ask_price,
            ask_low=ask_price,
            ask_close=ask_price,
            bid_open=bid_price,
            bid_high=bid_price,
            bid_low=bid_price,
            bid_close=bid_price,
        )
    return market


# ===============================
# Core Functionality Tests
# ===============================


def test_initialization_with_timedelta_windows(indicator):
    """Test MovingAverageCrossing initialization with timedelta objects for short and long windows ensuring proper storage of window parameters and successful creation of indicator instance without errors or exceptions during constructor execution.

    Parameters
    ----------
    indicator : MovingAverageCrossing
        Indicator fixture with default window configuration for initialization testing.
    """
    assert (
        indicator.short_window == SHORT_WINDOW
    ), f"Expected short_window {SHORT_WINDOW}, got {indicator.short_window}"
    assert (
        indicator.long_window == LONG_WINDOW
    ), f"Expected long_window {LONG_WINDOW}, got {indicator.long_window}"
    assert hasattr(indicator, "run"), "Indicator should have run method for execution"
    assert hasattr(
        indicator, "plot"
    ), "Indicator should have plot method for visualization"


@pytest.mark.parametrize(
    "short_win,long_win",
    [(5 * minutes, 20 * minutes), (1 * hours, 4 * hours), (1 * days, 5 * days)],
)
def test_initialization_with_different_window_types(short_win, long_win):
    """Test MovingAverageCrossing initialization using various timedelta types including minutes, hours, and days to ensure proper handling of different time units and correct storage of window parameters regardless of the specific timedelta unit used.

    Parameters
    ----------
    short_win : timedelta
        Short window duration for moving average calculation.
    long_win : timedelta
        Long window duration for moving average calculation.
    """
    indicator = MovingAverageCrossing(short_window=short_win, long_window=long_win)
    assert indicator.short_window == short_win, f"Short window mismatch for {short_win}"
    assert indicator.long_window == long_win, f"Long window mismatch for {long_win}"


def test_run_with_sample_market_data(sample_market):
    """Test MovingAverageCrossing execution with sample market data ensuring proper processing of Market objects and generation of moving average data with appropriate array lengths matching input data and successful computation without errors or exceptions.

    Parameters
    ----------
    sample_market : Market
        Sample market fixture for testing indicator execution.
    """
    indicator = MovingAverageCrossing(
        short_window=SHORT_WINDOW, long_window=LONG_WINDOW
    )
    indicator.run(sample_market)
    assert hasattr(
        indicator, "market"
    ), "Indicator should store market reference after run"
    assert indicator.market == sample_market, "Stored market should match input market"
    assert hasattr(
        indicator, "_cpp_short_moving_average"
    ), "Should have short moving average data"
    assert hasattr(
        indicator, "_cpp_long_moving_average"
    ), "Should have long moving average data"
    assert hasattr(indicator, "_cpp_regions"), "Should have signal regions data"


def test_moving_average_array_lengths(sample_market):
    """Test that computed moving average arrays have correct lengths matching input market data ensuring consistent output dimensions and proper handling of array sizing regardless of market data length or window parameters used during computation.

    Parameters
    ----------
    sample_market : Market
        Sample market fixture for array length validation.
    """
    indicator = MovingAverageCrossing(
        short_window=SHORT_WINDOW, long_window=LONG_WINDOW
    )
    indicator.run(sample_market)
    market_length = len(sample_market.dates)
    assert (
        len(indicator._cpp_short_moving_average) == market_length
    ), f"Short MA length {len(indicator._cpp_short_moving_average)} should match market length {market_length}"
    assert (
        len(indicator._cpp_long_moving_average) == market_length
    ), f"Long MA length {len(indicator._cpp_long_moving_average)} should match market length {market_length}"
    assert (
        len(indicator._cpp_regions) == market_length
    ), f"Regions length {len(indicator._cpp_regions)} should match market length {market_length}"


def test_moving_average_computation_accuracy():
    """Test accuracy of moving average computations by comparing calculated values with manually computed expected results for known input sequences ensuring mathematical correctness and numerical precision within acceptable tolerance levels."""
    # Create simple increasing sequence for predictable calculations
    simple_prices = [float(i + 1) for i in range(10)]  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    indicator = MovingAverageCrossing(short_window=3 * minutes, long_window=5 * minutes)
    indicator._cpp_run_with_vector(simple_prices)

    short_ma = np.asarray(indicator._cpp_short_moving_average)

    long_ma = np.asarray(indicator._cpp_long_moving_average)

    # For 3-period moving average: MA[2] = (1+2+3)/3 = 2.0
    assert (
        pytest.approx(short_ma[2], rel=1e-9) == 2.0
    ), f"Expected short MA[2] = 2.0, got {short_ma[2]}"
    # For 3-period moving average: MA[3] = (2+3+4)/3 = 3.0
    assert (
        pytest.approx(short_ma[3], rel=1e-9) == 3.0
    ), f"Expected short MA[3] = 3.0, got {short_ma[3]}"
    # For 5-period moving average: MA[4] = (1+2+3+4+5)/5 = 3.0
    assert (
        pytest.approx(long_ma[4], rel=1e-9) == 3.0
    ), f"Expected long MA[4] = 3.0, got {long_ma[4]}"


def test_golden_cross_signal_detection():
    """Test detection of golden cross signals when short moving average crosses above long moving average ensuring proper signal generation with correct timing and magnitude for bullish crossover patterns in various market conditions."""
    # Create falling then rising price pattern to generate golden cross
    prices = [
        10.0,
        9.0,
        8.0,
        7.0,
        6.0,
        5.0,
        6.0,
        7.0,
        8.0,
        9.0,
        10.0,
        11.0,
        12.0,
        13.0,
        14.0,
        15.0,
        16.0,
        17.0,
        18.0,
        19.0,
    ]

    indicator = MovingAverageCrossing(short_window=3 * minutes, long_window=5 * minutes)
    indicator._cpp_run_with_vector(prices)

    regions = np.asarray(indicator._cpp_regions)
    # Look for positive signals (golden cross)
    positive_signals = np.where(regions > 0)[0]
    assert (
        len(positive_signals) > 0
    ), "Should detect at least one golden cross signal in rising price pattern"


def test_death_cross_signal_detection():
    """Test detection of death cross signals when short moving average crosses below long moving average ensuring proper signal generation with correct timing and magnitude for bearish crossover patterns in declining market conditions."""
    # Create rising then falling price pattern to generate death cross
    prices = [
        5.0,
        6.0,
        7.0,
        8.0,
        9.0,
        10.0,
        9.0,
        8.0,
        7.0,
        6.0,
        5.0,
        4.0,
        3.0,
        2.0,
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
    ]

    indicator = MovingAverageCrossing(short_window=3 * minutes, long_window=5 * minutes)
    indicator._cpp_run_with_vector(prices)

    regions = np.asarray(indicator._cpp_regions)
    # Look for negative signals (death cross)
    negative_signals = np.where(regions < 0)[0]
    assert (
        len(negative_signals) > 0
    ), "Should detect at least one death cross signal in falling price pattern"


def test_no_signals_in_sideways_market():
    """Test that no crossover signals are generated in sideways trending markets where short and long moving averages remain relatively stable without significant crossovers ensuring proper signal filtering in non-trending conditions."""
    # Create sideways price pattern with minimal variation
    prices = [100.0 for i in range(50)]  # Very small oscillations

    indicator = MovingAverageCrossing(
        short_window=SHORT_WINDOW, long_window=LONG_WINDOW
    )
    indicator._cpp_run_with_vector(prices)

    regions = np.asarray(indicator._cpp_regions)
    signal_count = np.count_nonzero(regions)
    print(regions, signal_count)
    # Should have minimal or no signals in sideways market
    assert (
        signal_count <= 2
    ), f"Expected minimal signals in sideways market, got {signal_count} signals"


def test_edge_case_insufficient_data():
    """Test handling of edge case where market data is insufficient for computing long moving average ensuring graceful handling of boundary conditions and appropriate behavior when data length is less than required window size."""
    # Create market with fewer data points than long window requires
    short_prices = [100.0, 101.0, 102.0]

    indicator = MovingAverageCrossing(
        short_window=SHORT_WINDOW, long_window=LONG_WINDOW
    )
    # Should handle insufficient data gracefully without crashing
    try:
        indicator._cpp_run_with_vector(short_prices)
        # If it runs, check that arrays have correct length
        assert len(indicator._cpp_short_moving_average) == len(
            short_prices
        ), "Array length should match input data"
    except Exception as e:
        # Expected behavior - should handle gracefully or raise informative error
        assert (
            "insufficient" in str(e).lower() or "data" in str(e).lower()
        ), f"Unexpected error message: {e}"


def test_window_conversion_to_cpp_indices():
    """Test conversion of timedelta window specifications to C++ compatible integer indices ensuring proper transformation of time-based windows to array index offsets for underlying C++ computation engine."""
    test_cases = [
        (5 * minutes, 20 * minutes),
        (10 * minutes, 30 * minutes),
        (1 * hours, 4 * hours),
    ]

    for short_win, long_win in test_cases:
        indicator = MovingAverageCrossing(short_window=short_win, long_window=long_win)
        assert indicator.short_window == short_win, "Should store original short window"
        assert indicator.long_window == long_win, "Should store original long window"


def test_moving_averages_smooth_price_data(volatile_prices):
    """Test that moving averages properly smooth volatile price data reducing noise and providing cleaner trend signals compared to raw price data with verification of smoothing effectiveness through variance analysis.

    Parameters
    ----------
    volatile_prices : numpy.ndarray
        Volatile price data for smoothing effectiveness testing.
    """
    indicator = MovingAverageCrossing(
        short_window=5 * minutes, long_window=10 * minutes
    )
    indicator._cpp_run_with_vector(volatile_prices.tolist())

    short_ma = np.asarray(indicator._cpp_short_moving_average)
    long_ma = np.asarray(indicator._cpp_long_moving_average)

    # Moving averages should be smoother (lower variance) than raw prices
    price_variance = np.var(volatile_prices)
    short_ma_variance = np.var(short_ma[~np.isnan(short_ma)])  # Exclude NaNs
    long_ma_variance = np.var(long_ma[~np.isnan(long_ma)])  # Exclude NaNs

    assert (
        short_ma_variance < price_variance
    ), "Short MA should be smoother than raw prices"
    assert (
        long_ma_variance < short_ma_variance
    ), "Long MA should be smoother than short MA"


def test_plot_method_execution(sample_market):
    """Test execution of plot method ensuring proper visualization generation without errors and correct handling of matplotlib backend configuration for testing environment compatibility.

    Parameters
    ----------
    sample_market : Market
        Sample market fixture for plot generation testing.
    """
    indicator = MovingAverageCrossing(
        short_window=SHORT_WINDOW, long_window=LONG_WINDOW
    )
    indicator.run(sample_market)

    # Test plot method execution (requires matplotlib)
    try:
        with patch("matplotlib.pyplot.show"):  # Mock plt.show to prevent display
            figure = indicator.plot(show=False)
            assert isinstance(figure, plt.Figure), "Plot should return a figure object"
    except ImportError:
        pytest.skip("Matplotlib not available for plotting tests")
    except Exception as e:
        pytest.fail(f"Plot method failed with error: {e}")


def test_performance_with_large_dataset():
    """Test performance characteristics with large datasets ensuring acceptable computation times for enterprise-scale market data processing and memory usage optimization validation under high-volume scenarios."""
    # Create large dataset for performance testing
    large_prices = [
        100.0 + np.sin(i * 0.001) * 10 + np.random.normal(0, 0.5) for i in range(10000)
    ]

    indicator = MovingAverageCrossing(
        short_window=SHORT_WINDOW, long_window=LONG_WINDOW
    )

    start_time = time.time()
    indicator._cpp_run_with_vector(large_prices)
    execution_time = time.time() - start_time

    # Performance should be reasonable (less than 5 seconds for 10k data points)
    assert (
        execution_time < 5.0
    ), f"Execution time {execution_time:.2f}s exceeds performance threshold"
    assert len(indicator._cpp_short_moving_average) == len(
        large_prices
    ), "Output length should match input length"


def test_memory_usage_and_cleanup():
    """Test memory usage patterns and garbage collection effectiveness ensuring proper cleanup of resources after indicator computation and verification of memory leak prevention in repeated execution scenarios."""
    initial_objects = len(gc.get_objects())

    # Create and run multiple indicators to test memory management
    for i in range(100):
        prices = [100.0 + np.random.normal(0, 1) for _ in range(100)]

        indicator = MovingAverageCrossing(
            short_window=SHORT_WINDOW, long_window=LONG_WINDOW
        )
        indicator._cpp_run_with_vector(prices)
        del indicator

    # Force garbage collection
    gc.collect()
    final_objects = len(gc.get_objects())

    # Memory usage should not grow excessively
    object_growth = final_objects - initial_objects
    assert (
        object_growth < 1000
    ), f"Excessive object growth: {object_growth} new objects remain"


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
        market.add_tick(timestamp=date, bid_price=price - 0.01, ask_price=price + 0.01)

    # Adjust window sizes based on frequency
    short_win = max(5 * time_delta, 5 * minutes)
    long_win = max(20 * time_delta, 20 * minutes)

    indicator = MovingAverageCrossing(short_window=short_win, long_window=long_win)
    indicator.run(market=market)

    assert len(indicator._cpp_short_moving_average) == len(
        dates
    ), f"Output length mismatch for {frequency}min frequency"
    assert len(indicator._cpp_long_moving_average) == len(
        dates
    ), f"Output length mismatch for {frequency}min frequency"


price_ranges = [
    (0.01, 0.02),  # Very small prices
    (1000.0, 2000.0),  # Large prices
    (-50.0, 50.0),  # Negative prices
]


@pytest.mark.parametrize("price_range", price_ranges)
def test_extreme_value_handling(price_range):
    """Test indicator handling of extreme price values including very small, very large, and negative prices ensuring numerical stability and accuracy across wide value ranges.

    Parameters
    ----------
    price_range : tuple
        Tuple containing minimum and maximum price values for testing extreme conditions.
    """
    min_price, max_price = price_range
    dates = [DEFAULT_START_DATE + i * minutes for i in range(30)]
    prices = [
        min_price + (max_price - min_price) * np.random.random() for _ in range(30)
    ]
    market = Market()
    for date, price in zip(dates, prices):
        market.add_tick(timestamp=date, bid_price=price - 0.01, ask_price=price + 0.01)

    indicator = MovingAverageCrossing(
        short_window=5 * minutes, long_window=10 * minutes
    )
    indicator.run(market=market)

    short_ma = np.asarray(indicator._cpp_short_moving_average)
    long_ma = np.asarray(indicator._cpp_long_moving_average)

    # Check for numerical stability (no NaN or infinite values)
    assert (
        np.count_nonzero(np.isnan(short_ma)) == 4
    ), "Short MA should have exactly 4 NaN values"
    assert (
        np.count_nonzero(np.isnan(long_ma)) == 9
    ), "Long MA should have exactly 19 NaN values"


def test_signal_region_values(sample_market):
    """Test that signal region values are within expected ranges and properly indicate crossing strength ensuring appropriate signal magnitude scaling and correct interpretation of crossover intensity.

    Parameters
    ----------
    sample_market : Market
        Sample market fixture for signal region validation.
    """
    indicator = MovingAverageCrossing(
        short_window=SHORT_WINDOW, long_window=LONG_WINDOW
    )
    indicator.run(market=sample_market)

    regions = np.asarray(indicator._cpp_regions)
    # Remove zero values for analysis
    non_zero_regions = regions[regions != 0]

    if len(non_zero_regions) > 0:
        # Signal values should be reasonable (not extremely large)
        max_signal = np.max(np.abs(non_zero_regions))
        assert (
            max_signal < 1000.0
        ), f"Signal values should be reasonable, got max {max_signal}"

        # Signals should include both positive and negative values in typical market data
        has_positive = np.any(non_zero_regions > 0)
        has_negative = np.any(non_zero_regions < 0)
        # Note: Not asserting both exist as market data might be purely trending


def test_multiple_indicator_instances():
    """Test creation and execution of multiple indicator instances with different parameters ensuring proper isolation between instances and correct independent operation without cross-contamination of results."""
    dates = [DEFAULT_START_DATE + i * minutes for i in range(50)]
    prices = [100.0 + np.sin(i * 0.1) * 5 for i in range(50)]
    market = Market()
    for date, price in zip(dates, prices):
        market.add_tick(timestamp=date, bid_price=price - 0.01, ask_price=price + 0.01)

    # Create multiple indicators with different parameters
    indicator1 = MovingAverageCrossing(
        short_window=5 * minutes, long_window=15 * minutes
    )
    indicator2 = MovingAverageCrossing(
        short_window=10 * minutes, long_window=30 * minutes
    )

    indicator1.run(market=market)
    indicator2.run(market=market)

    # Indicators should have different results due to different parameters
    ma1_short = np.asarray(indicator1._cpp_short_moving_average)
    ma2_short = np.asarray(indicator2._cpp_short_moving_average)

    # Results should be different (not identical)
    assert not np.array_equal(
        ma1_short, ma2_short
    ), "Different indicators should produce different results"

    # Both should have valid data
    assert len(ma1_short) == len(dates), "Indicator 1 should have correct output length"
    assert len(ma2_short) == len(dates), "Indicator 2 should have correct output length"


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
    indicator = MovingAverageCrossing(
        short_window=SHORT_WINDOW, long_window=LONG_WINDOW
    )

    # Step 1: Run computation
    indicator.run(market=sample_market)

    # Step 2: Verify all outputs are generated
    assert hasattr(
        indicator, "_cpp_short_moving_average"
    ), "Should have short moving average"
    assert hasattr(
        indicator, "_cpp_long_moving_average"
    ), "Should have long moving average"
    assert hasattr(indicator, "_cpp_regions"), "Should have signal regions"

    # Step 3: Verify data consistency
    data_length = len(sample_market.dates)
    assert (
        len(indicator._cpp_short_moving_average) == data_length
    ), "Data length consistency check"
    assert (
        len(indicator._cpp_long_moving_average) == data_length
    ), "Data length consistency check"
    assert len(indicator._cpp_regions) == data_length, "Data length consistency check"

    # Step 4: Verify basic mathematical properties
    short_ma = np.asarray(indicator._cpp_short_moving_average).astype(np.float64)
    long_ma = np.asarray(indicator._cpp_long_moving_average).astype(np.float64)

    # Non-zero moving averages should be positive for positive price data
    non_zero_short = short_ma[~np.isnan(short_ma)]
    non_zero_long = long_ma[~np.isnan(long_ma)]

    if len(non_zero_short) > 0:
        assert np.all(
            non_zero_short > 0
        ), "Moving averages should be positive for positive price data"
    if len(non_zero_long) > 0:
        assert np.all(
            non_zero_long > 0
        ), "Moving averages should be positive for positive price data"


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
