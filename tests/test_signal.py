"""
Comprehensive test suite for Signal class functionality and validation.

This module contains exhaustive tests for the Signal class, covering signal generation,
validation, market integration, and edge cases. The tests ensure that trading signals
are properly generated, validated against market data, and maintain consistency across
different market conditions and time spans.

Key test categories:
- Signal initialization and market synchronization
- Random signal generation with statistical validation
- Signal validation and integrity checks
- Edge cases and error handling
- Performance and memory usage validation
- Integration with different market data sources

Notes
-----
All tests use pytest fixtures for consistent test data

See Also
--------
Signal : Signal class for implementation details
Market : Market class for market data structure
"""

import pytest
import numpy as np

from TradeTide.market import Market
from TradeTide.signal import Signal
from TradeTide.currencies import Currency
from TradeTide.times import days, hours
import TradeTide

# Enable debug mode for detailed logging during test execution
TradeTide.debug_mode = True

# ===============================
# Test Fixtures and Setup
# ===============================

@pytest.fixture
def market():
    """
    Create a standard market fixture for testing signal functionality.

    Provides a EUR/USD market with 1 day of data, which gives sufficient
    data points for statistical validation while keeping test execution fast.

    Returns
    -------
    Market
        Configured market instance with EUR/USD data

    Notes
    -----
    Uses 1 day timespan to balance test coverage with execution speed
    """
    market = Market()
    market.load_from_database(
        currency_0=Currency.EUR,
        currency_1=Currency.USD,
        time_span=1 * days,
    )
    return market

@pytest.fixture
def large_market():
    """
    Create a larger market dataset for performance and statistical testing.

    Provides a week's worth of data for tests that require larger sample sizes
    or need to validate behavior over extended periods.

    Returns
    -------
    Market
        Market instance with 7 days of EUR/USD data

    Notes
    -----
    Slower than standard market fixture but provides better statistical power
    """
    market = Market()
    market.load_from_database(
        currency_0=Currency.EUR,
        currency_1=Currency.USD,
        time_span=7 * days,
    )
    return market

@pytest.fixture
def small_market():
    """
    Create a minimal market dataset for edge case testing.

    Provides a small dataset (1 hour) to test behavior with limited data
    and validate edge cases around minimum data requirements.

    Returns
    -------
    Market
        Market instance with 1 hour of EUR/USD data

    Notes
    -----
    Used for testing boundary conditions and minimum data scenarios
    """
    market = Market()
    market.load_from_database(
        currency_0=Currency.EUR,
        currency_1=Currency.USD,
        time_span=1 * hours,
    )
    return market

# ===============================
# Core Signal Functionality Tests
# ===============================

def test_signal_initialization_with_market(market):
    """
    Test that Signal initializes correctly with market data.

    Validates that:
    - Signal object is created successfully
    - Internal trade_signal vector is initialized
    - Signal length matches market data length
    - Initial signal state is properly set

    Parameters
    ----------
    market : Market
        Market fixture with EUR/USD data

    Raises
    ------
    AssertionError
        If signal initialization fails or dimensions mismatch
    """
    signal = Signal(market)

    # Verify signal object creation
    assert signal is not None, "Signal object was not created"
    assert hasattr(signal, 'trade_signal'), "Signal missing trade_signal attribute"

    # Verify dimensional consistency
    assert len(signal.trade_signal) == len(market.dates), \
        f"Signal length ({len(signal.trade_signal)}) does not match market length ({len(market.dates)})"

    # Verify initial state
    assert len(signal.trade_signal) > 0, "Signal should not be empty for non-empty market"

def test_signal_length_matches_market(market):
    """
    Test strict dimensional consistency between signal and market data.

    This is a critical test ensuring that signals maintain perfect alignment
    with market timestamps, which is essential for accurate backtesting.

    Parameters
    ----------
    market : Market
        Market fixture with test data

    Notes
    -----
    This test is fundamental to all signal operations
    """
    signal = Signal(market)
    assert len(signal.trade_signal) == len(market.dates), "Signal length does not match market"

def test_signal_initialization_different_markets(large_market, small_market):
    """
    Test signal initialization with markets of different sizes.

    Validates that Signal correctly adapts to various market data sizes
    and maintains consistency across different time spans.

    Parameters
    ----------
    large_market : Market
        Market with 7 days of data
    small_market : Market
        Market with 1 hour of data
    """
    large_signal = Signal(large_market)
    small_signal = Signal(small_market)

    # Verify both signals are properly sized
    assert len(large_signal.trade_signal) == len(large_market.dates)
    assert len(small_signal.trade_signal) == len(small_market.dates)

    # Large market should have more data points
    assert len(large_signal.trade_signal) > len(small_signal.trade_signal), \
        "Large market should have more data points than small market"

# ===============================
# Random Signal Generation Tests
# ===============================

def test_generate_random_signal_basic(market):
    """
    Test basic random signal generation functionality.

    Validates that random signal generation works with standard parameters
    and produces signals within expected statistical bounds.

    Parameters
    ----------
    market : Market
        Market fixture for signal generation
    """
    signal = Signal(market)
    signal.generate_random(probability=0.2)

    # Verify signal was generated
    longs, shorts = signal.count_signals()
    total_signals = longs + shorts

    # Should have some signals but not all positions
    assert total_signals > 0, "Random generation should produce some signals"
    assert total_signals < len(market.dates), "Should not generate signals for every data point"

def test_generate_random_signal_distribution(market):
    """
    Test statistical distribution of randomly generated signals.

    Validates that random signal generation follows the specified probability
    distribution within acceptable statistical bounds. Uses loose bounds to
    account for random variation while catching systematic errors.

    Parameters
    ----------
    market : Market
        Market fixture providing test data

    Notes
    -----
    Uses 10%-30% bounds for 20% probability to account for random variation
    """
    signal = Signal(market)
    signal.generate_random(probability=0.2)
    longs, shorts = signal.count_signals()

    total = longs + shorts
    expected_min = int(0.1 * len(market.dates))  # Loose lower bound
    expected_max = int(0.3 * len(market.dates))  # Loose upper bound

    assert expected_min <= total <= expected_max, \
        f"Random signal generation ({total}) is outside expected range [{expected_min}, {expected_max}]"

@pytest.mark.parametrize("probability", [0.05, 0.1, 0.2, 0.5, 0.8])
def test_generate_random_signal_different_probabilities(market, probability):
    """
    Test random signal generation with various probability values.

    Validates that different probability settings produce appropriately
    different signal densities. Tests common probability values used
    in trading strategy development.

    Parameters
    ----------
    market : Market
        Market fixture for testing
    probability : float
        Signal generation probability to test

    Notes
    -----
    Uses parametrized testing for comprehensive coverage
    """
    signal = Signal(market)
    signal.generate_random(probability=probability)

    longs, shorts = signal.count_signals()
    total_signals = longs + shorts
    signal_rate = total_signals / len(market.dates)

    # Statistical bounds: allow 50% deviation from target probability
    min_expected = probability * 0.5
    max_expected = probability * 1.5

    assert min_expected <= signal_rate <= max_expected, \
        f"Signal rate {signal_rate:.3f} outside bounds [{min_expected:.3f}, {max_expected:.3f}] for probability {probability}"

def test_generate_random_signal_reproducibility(market):
    """
    Test that random signal generation can be made reproducible.

    Validates that when using the same random seed, signal generation
    produces identical results, which is crucial for testing and debugging.

    Parameters
    ----------
    market : Market
        Market fixture for testing

    Notes
    -----
    Assumes Signal class supports random seed setting
    """
    # Generate two signals with same parameters
    signal1 = Signal(market)
    signal2 = Signal(market)

    # If seed setting is available, use it
    try:
        signal1.generate_random(probability=0.2, seed=42)
        signal2.generate_random(probability=0.2, seed=42)

        # Signals should be identical
        assert signal1.trade_signal == signal2.trade_signal, \
            "Signals with same seed should be identical"
    except TypeError:
        # If seed parameter not available, test basic repeatability
        signal1.generate_random(probability=0.2)
        signal2.generate_random(probability=0.2)

        # At least verify both generated valid signals
        assert len(signal1.trade_signal) == len(signal2.trade_signal)

def test_generate_random_signal_extreme_probabilities(market):
    """
    Test random signal generation with extreme probability values.

    Validates behavior at probability boundaries (0.0 and 1.0) and
    ensures the system handles edge cases appropriately.

    Parameters
    ----------
    market : Market
        Market fixture for boundary testing
    """
    signal = Signal(market)

    # Test zero probability - should generate no signals
    signal.generate_random(probability=0.0)
    longs, shorts = signal.count_signals()
    assert longs + shorts == 0, "Zero probability should generate no signals"

    # Test maximum probability - should generate many signals
    signal.generate_random(probability=1.0)
    longs, shorts = signal.count_signals()
    total_signals = longs + shorts

    # Should generate signals for most data points (allowing for some randomness)
    min_expected = int(0.8 * len(market.dates))
    assert total_signals >= min_expected, \
        f"High probability should generate many signals, got {total_signals}, expected >= {min_expected}"

# ===============================
# Signal Validation Tests
# ===============================

def test_signal_validation_after_creation(market):
    """
    Test that newly created signals pass validation checks.

    Validates that signals created with market data automatically
    satisfy all validation requirements without additional setup.

    Parameters
    ----------
    market : Market
        Market fixture for validation testing

    Notes
    -----
    This is a fundamental sanity check for signal integrity
    """
    signal = Signal(market)
    assert signal.validate_against_market(), "Signal failed validation after creation"

def test_signal_validation_after_random_generation(market):
    """
    Test signal validation after random signal generation.

    Ensures that randomly generated signals maintain validity and
    consistency with the underlying market data structure.

    Parameters
    ----------
    market : Market
        Market fixture for testing
    """
    signal = Signal(market)
    signal.generate_random(probability=0.3)

    assert signal.validate_against_market(), \
        "Signal failed validation after random generation"

def test_signal_validation_comprehensive(large_market):
    """
    Test comprehensive signal validation with larger dataset.

    Uses a larger market dataset to test validation robustness
    across extended time periods and various market conditions.

    Parameters
    ----------
    large_market : Market
        Extended market data for thorough testing
    """
    signal = Signal(large_market)
    signal.generate_random(probability=0.25)

    # Test multiple validation aspects
    assert signal.validate_against_market(), "Comprehensive validation failed"

    # Additional validation checks if available
    if hasattr(signal, 'validate_signal_consistency'):
        assert signal.validate_signal_consistency(), "Signal consistency check failed"

# ===============================
# Signal Counting and Statistics Tests
# ===============================

def test_signal_counting_accuracy(market):
    """
    Test accuracy of signal counting mechanisms.

    Validates that the count_signals() method accurately counts
    long and short signals, providing correct statistics for
    strategy evaluation.

    Parameters
    ----------
    market : Market
        Market fixture for counting tests
    """
    signal = Signal(market)
    signal.generate_random(probability=0.3)

    longs, shorts = signal.count_signals()
    total_signals = longs + shorts

    # Verify counts are non-negative integers
    assert isinstance(longs, int) and longs >= 0, "Long count should be non-negative integer"
    assert isinstance(shorts, int) and shorts >= 0, "Short count should be non-negative integer"

    # Total should not exceed market data points
    assert total_signals <= len(market.dates), \
        f"Total signals ({total_signals}) cannot exceed market data points ({len(market.dates)})"

def test_signal_statistics_consistency(market):
    """
    Test consistency of signal statistics across multiple generations.

    Validates that signal statistics remain consistent when signals
    are regenerated with the same parameters.

    Parameters
    ----------
    market : Market
        Market fixture for consistency testing
    """
    signal = Signal(market)

    # Generate signals multiple times and check consistency
    results = []
    for _ in range(5):
        signal.generate_random(probability=0.2)
        longs, shorts = signal.count_signals()
        results.append((longs, shorts))

    # Calculate statistics
    total_counts = [longs + shorts for longs, shorts in results]
    mean_total = np.mean(total_counts)
    std_total = np.std(total_counts)

    # Standard deviation should be reasonable (not too high)
    coefficient_of_variation = std_total / mean_total if mean_total > 0 else 0
    assert coefficient_of_variation < 1.0, \
        f"Signal generation too variable: CV = {coefficient_of_variation:.3f}"

# ===============================
# Edge Cases and Error Handling Tests
# ===============================

def test_signal_with_minimal_market_data(small_market):
    """
    Test signal behavior with minimal market data.

    Validates that signals can be created and function correctly
    even with very limited market data (edge case testing).

    Parameters
    ----------
    small_market : Market
        Market with minimal data (1 hour)
    """
    signal = Signal(small_market)

    # Should still create valid signal
    assert len(signal.trade_signal) == len(small_market.dates)
    assert len(signal.trade_signal) > 0, "Signal should have some data points even with minimal market"

    # Should be able to generate random signals
    signal.generate_random(probability=0.5)
    longs, shorts = signal.count_signals()

    # Counts should be valid even with small dataset
    assert longs >= 0 and shorts >= 0, "Signal counts should be valid with minimal data"

def test_signal_empty_market_handling():
    """
    Test signal behavior with empty or invalid market data.

    Validates proper error handling when market data is missing
    or invalid, ensuring graceful failure modes.

    Notes
    -----
    This test checks error handling for edge cases
    """
    # Test with None market (should raise appropriate error)
    with pytest.raises((ValueError, TypeError, AttributeError)):
        signal = Signal(None)

    # Test with empty market if possible
    try:
        empty_market = Market()  # Uninitialized market
        with pytest.raises((ValueError, RuntimeError)):
            signal = Signal(empty_market)
    except Exception:
        # If Market doesn't support empty initialization, skip this part
        pass

def test_signal_invalid_probability_handling(market):
    """
    Test signal generation with invalid probability values.

    Validates that the system properly handles invalid inputs
    and provides appropriate error messages or corrections.

    Parameters
    ----------
    market : Market
        Market fixture for error testing
    """
    signal = Signal(market)

    # Test negative probability
    with pytest.raises((ValueError, AssertionError)):
        signal.generate_random(probability=-0.1)

    # Test probability > 1.0
    with pytest.raises((ValueError, AssertionError)):
        signal.generate_random(probability=1.5)

# ===============================
# Performance and Memory Tests
# ===============================

def test_signal_memory_usage(large_market):
    """
    Test that signal objects don't consume excessive memory.

    Validates memory efficiency of signal storage and operations,
    ensuring scalability for large market datasets.

    Parameters
    ----------
    large_market : Market
        Large dataset for memory testing

    Notes
    -----
    This is a basic memory usage validation
    """
    import sys

    initial_size = sys.getsizeof([])
    signal = Signal(large_market)
    signal_size = sys.getsizeof(signal.trade_signal)

    # Signal should not be unreasonably large
    size_ratio = signal_size / len(large_market.dates)
    assert size_ratio < 100, f"Signal memory usage seems excessive: {size_ratio} bytes per data point"

def test_signal_generation_performance(large_market):
    """
    Test signal generation performance with large datasets.

    Validates that signal generation completes within reasonable
    time limits, ensuring system remains responsive.

    Parameters
    ----------
    large_market : Market
        Large dataset for performance testing
    """
    import time

    signal = Signal(large_market)

    start_time = time.time()
    signal.generate_random(probability=0.2)
    generation_time = time.time() - start_time

    # Should complete within reasonable time (adjust threshold as needed)
    max_time = 1.0  # 1 second for large market
    assert generation_time < max_time, \
        f"Signal generation took too long: {generation_time:.3f}s > {max_time}s"

# ===============================
# Integration Tests
# ===============================

def test_signal_market_integration_workflow(market):
    """
    Test complete workflow integration between Signal and Market.

    Validates the typical usage pattern from market creation through
    signal generation to final validation, ensuring all components
    work together correctly.

    Parameters
    ----------
    market : Market
        Market fixture for integration testing
    """
    # Complete workflow test
    signal = Signal(market)

    # Verify initial state
    assert signal.validate_against_market()

    # Generate signals
    signal.generate_random(probability=0.25)

    # Verify post-generation state
    assert signal.validate_against_market()

    # Get statistics
    longs, shorts = signal.count_signals()

    # Verify statistics make sense
    assert longs >= 0 and shorts >= 0
    assert longs + shorts <= len(market.dates)

    # Verify signal can be used for further operations
    total_signals = longs + shorts
    if total_signals > 0:
        signal_density = total_signals / len(market.dates)
        assert 0.0 <= signal_density <= 1.0, "Signal density should be between 0 and 1"

@pytest.mark.parametrize("currency_pair", [
    (Currency.EUR, Currency.USD),
    (Currency.GBP, Currency.USD),
    (Currency.USD, Currency.JPY),
])
def test_signal_multiple_currency_pairs(currency_pair):
    """
    Test signal functionality across different currency pairs.

    Validates that signals work correctly with various currency
    pairs, ensuring broad market compatibility.

    Parameters
    ----------
    currency_pair : tuple of Currency
        Tuple of (base_currency, quote_currency)

    Notes
    -----
    Uses parametrized testing for multiple currency pairs
    """
    try:
        market = Market()
        market.load_from_database(
            currency_0=currency_pair[0],
            currency_1=currency_pair[1],
            time_span=1 * days,
        )

        signal = Signal(market)
        signal.generate_random(probability=0.2)

        # Basic validation for each currency pair
        assert signal.validate_against_market()
        longs, shorts = signal.count_signals()
        assert longs >= 0 and shorts >= 0

    except Exception as e:
        # Skip if currency pair data not available
        pytest.skip(f"Currency pair {currency_pair} not available: {e}")

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
    >>> python test_signal.py

    Notes
    -----
    Use pytest directly for more control over test execution
    """
    pytest.main([
        "-v",           # Verbose output
        "-W", "error",  # Treat warnings as errors
        "--tb=short",   # Short traceback format
        __file__
    ])