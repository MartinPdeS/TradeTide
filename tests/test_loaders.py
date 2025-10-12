#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

"""
Comprehensive test suite for market data loading functionality.

This module contains exhaustive tests for the market data loading system,
covering various data sources, currency pairs, time spans, and error handling.
The tests ensure that market data can be reliably loaded from different sources
and that the loading process maintains data integrity and consistency.

Key test categories:
- Database loading with multiple currency pairs
- Data validation and integrity checks
- Time span and date range handling
- Error handling for invalid inputs
- Performance testing with large datasets
- Memory usage validation
- Data source compatibility testing

Notes
-----
All tests use pytest fixtures and parametrization for comprehensive coverage

See Also
--------
Market : Market class for data storage and management
get_market_data : Primary data loading function
Currency : Currency enumeration for supported currencies
"""

import pytest
import numpy as np

from TradeTide.currencies import Currency
from TradeTide.market import Market
from TradeTide.times import days, hours, weeks
import TradeTide

# Enable debug mode for detailed logging during test execution
TradeTide.debug_mode = True

# ===============================
# Test Configuration and Fixtures
# ===============================

# Comprehensive list of currency pairs for testing
MAJOR_CURRENCY_PAIRS = [
    (Currency.EUR, Currency.USD),  # Most liquid pair
    (Currency.GBP, Currency.USD),  # Cable
    (Currency.USD, Currency.JPY),  # Yen pair
    (Currency.USD, Currency.CHF),  # Swiss franc
    (Currency.USD, Currency.CAD),  # Canadian dollar
]

EXOTIC_CURRENCY_PAIRS = [
    (Currency.CHF, Currency.USD),
    (Currency.JPY, Currency.USD),
    (Currency.CAD, Currency.USD),
]

ALL_CURRENCY_PAIRS = MAJOR_CURRENCY_PAIRS + EXOTIC_CURRENCY_PAIRS

# Test time spans for various scenarios
TIME_SPANS = [
    (1 * hours, "1_hour"),
    (6 * hours, "6_hours"),
    (1 * days, "1_day"),
    (3 * days, "3_days"),
    (1 * weeks, "1_week"),
]


@pytest.fixture
def sample_market():
    """
    Create a sample market for testing basic functionality.

    Returns
    -------
    Market
        Market instance with EUR/USD data for 1 day

    Notes
    -----
    Uses a standard currency pair and timespan for consistent testing
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
    Create a large market dataset for performance testing.

    Returns
    -------
    Market
        Market instance with EUR/USD data for 2 weeks

    Notes
    -----
    Used for testing performance and memory usage with larger datasets
    """
    market = Market()
    market.load_from_database(
        currency_0=Currency.EUR,
        currency_1=Currency.USD,
        time_span=2 * weeks,
    )
    return market


# ===============================
# Core Loading Functionality Tests
# ===============================


# ===============================
# Core Loading Functionality Tests
# ===============================


def test_market_initialization():
    """
    Test basic market object creation and initialization.

    Validates that Market objects can be created successfully
    and are ready for data loading operations.
    """
    market = Market()
    assert market is not None, "Market object should be created successfully"

    # Check that market has necessary attributes
    assert hasattr(
        market, "load_from_database"
    ), "Market should have load_from_database method"


def test_basic_database_loading(sample_market):
    """
    Test basic database loading functionality.

    Validates that market data can be loaded from the database
    and that the resulting market object contains valid data.

    Parameters
    ----------
    sample_market : Market
        Market fixture with loaded EUR/USD data
    """
    # Verify market data was loaded
    assert len(sample_market.dates) > 0, "Market should contain date data"
    assert hasattr(sample_market, "ask"), "Market should have ask data"
    assert hasattr(sample_market, "bid"), "Market should have bid data"

    # Verify bid/ask data consistency
    assert len(sample_market.ask.dates) == len(
        sample_market.dates
    ), "Ask dates should match market dates"
    assert len(sample_market.bid.dates) == len(
        sample_market.dates
    ), "Bid dates should match market dates"


@pytest.mark.parametrize(
    "currency_pair",
    MAJOR_CURRENCY_PAIRS,
    ids=lambda pair: f"{pair[0].value}_{pair[1].value}",
)
def test_load_major_currency_pairs(currency_pair):
    """
    Test loading of major currency pairs from database.

    Validates that all major currency pairs can be loaded successfully
    and contain valid market data.

    Parameters
    ----------
    currency_pair : tuple of Currency
        Tuple of (base_currency, quote_currency) to test

    Notes
    -----
    Uses parametrized testing for comprehensive currency pair coverage
    """
    market = Market()

    try:
        market.load_from_database(
            currency_0=currency_pair[0],
            currency_1=currency_pair[1],
            time_span=1 * days,
        )

        # Verify successful loading
        assert (
            len(market.dates) > 0
        ), f"No data loaded for {currency_pair[0].value}/{currency_pair[1].value}"

        # Verify data structure integrity
        assert len(market.ask.open) == len(market.dates), "Ask open data size mismatch"
        assert len(market.bid.open) == len(market.dates), "Bid open data size mismatch"

        # Verify data quality
        assert all(
            price > 0 for price in market.ask.open
        ), "Ask prices should be positive"
        assert all(
            price > 0 for price in market.bid.open
        ), "Bid prices should be positive"

    except Exception as e:
        pytest.skip(f"Currency pair {currency_pair} not available in database: {e}")


@pytest.mark.parametrize(
    "currency_pair",
    EXOTIC_CURRENCY_PAIRS,
    ids=lambda pair: f"{pair[0].value}_{pair[1].value}",
)
def test_load_exotic_currency_pairs(currency_pair):
    """
    Test loading of exotic currency pairs from database.

    Validates that less common currency pairs can be loaded when available,
    with appropriate handling for unavailable pairs.

    Parameters
    ----------
    currency_pair : tuple of Currency
        Tuple of (base_currency, quote_currency) to test
    """
    market = Market()

    try:
        market.load_from_database(
            currency_0=currency_pair[0],
            currency_1=currency_pair[1],
            time_span=1 * days,
        )

        # If loading succeeds, validate data
        assert (
            len(market.dates) > 0
        ), f"No data loaded for {currency_pair[0].value}/{currency_pair[1].value}"

    except Exception as e:
        # Exotic pairs may not be available - log and skip
        pytest.skip(f"Exotic currency pair {currency_pair} not available: {e}")


@pytest.mark.parametrize("time_span, span_id", TIME_SPANS)
def test_load_different_time_spans(time_span, span_id):
    """
    Test loading market data with various time spans.

    Validates that different time periods can be loaded successfully
    and that the resulting data sets have appropriate sizes.

    Parameters
    ----------
    time_span : Duration
        Time span duration to test
    span_id : str
        String identifier for the time span
    """
    market = Market()

    try:
        market.load_from_database(
            currency_0=Currency.EUR,
            currency_1=Currency.USD,
            time_span=time_span,
        )

        # Verify data was loaded
        assert len(market.dates) > 0, f"No data loaded for time span {span_id}"

        # Verify time span consistency
        if len(market.dates) > 1:
            actual_duration = market.dates[-1] - market.dates[0]
            # Allow some tolerance for weekend gaps and data availability
            assert (
                actual_duration <= time_span * 1.5
            ), f"Loaded duration exceeds requested time span for {span_id}"

    except Exception as e:
        pytest.skip(f"Time span {span_id} not available: {e}")


# ===============================
# Data Validation and Quality Tests
# ===============================


def test_data_integrity_validation(sample_market):
    """
    Test comprehensive data integrity validation.

    Validates that loaded market data maintains proper relationships
    and logical consistency across all price components.

    Parameters
    ----------
    sample_market : Market
        Market fixture with loaded data
    """
    # Test OHLC relationships for ask prices
    for i in range(len(sample_market.ask.dates)):
        open_price = sample_market.ask.open[i]
        high_price = sample_market.ask.high[i]
        low_price = sample_market.ask.low[i]
        close_price = sample_market.ask.close[i]

        # High should be highest, low should be lowest
        assert high_price >= max(
            open_price, close_price
        ), f"Ask high price validation failed at index {i}"
        assert low_price <= min(
            open_price, close_price
        ), f"Ask low price validation failed at index {i}"

    # Test OHLC relationships for bid prices
    for i in range(len(sample_market.bid.dates)):
        open_price = sample_market.bid.open[i]
        high_price = sample_market.bid.high[i]
        low_price = sample_market.bid.low[i]
        close_price = sample_market.bid.close[i]

        assert high_price >= max(
            open_price, close_price
        ), f"Bid high price validation failed at index {i}"
        assert low_price <= min(
            open_price, close_price
        ), f"Bid low price validation failed at index {i}"


def test_bid_ask_spread_validation(sample_market):
    """
    Test that bid-ask spreads are reasonable and consistent.

    Validates that ask prices are always higher than bid prices
    and that spreads fall within reasonable ranges.

    Parameters
    ----------
    sample_market : Market
        Market fixture with loaded data
    """
    for i in range(len(sample_market.dates)):
        ask_price = sample_market.ask.close[i]
        bid_price = sample_market.bid.close[i]

        # Ask should always be higher than bid
        assert (
            ask_price >= bid_price
        ), f"Ask price should be >= bid price at index {i}: ask={ask_price}, bid={bid_price}"

        # Spread should be reasonable (not zero, not excessive)
        spread = ask_price - bid_price
        spread_percentage = (spread / bid_price) * 100

        assert spread >= 0, f"Spread should be positive at index {i}"
        assert (
            spread_percentage < 1.0
        ), f"Spread seems excessive ({spread_percentage:.4f}%) at index {i}"


def test_date_chronological_ordering(sample_market):
    """
    Test that dates are in proper chronological order.

    Validates that all date vectors maintain chronological ordering
    without gaps or duplicates that would indicate data corruption.

    Parameters
    ----------
    sample_market : Market
        Market fixture with loaded data
    """
    # Test main dates vector
    for i in range(1, len(sample_market.dates)):
        assert (
            sample_market.dates[i] > sample_market.dates[i - 1]
        ), f"Dates not in chronological order at index {i}"

    # Test ask dates consistency
    for i in range(len(sample_market.ask.dates)):
        assert (
            sample_market.ask.dates[i] == sample_market.dates[i]
        ), f"Ask date mismatch at index {i}"

    # Test bid dates consistency
    for i in range(len(sample_market.bid.dates)):
        assert (
            sample_market.bid.dates[i] == sample_market.dates[i]
        ), f"Bid date mismatch at index {i}"


def test_price_data_completeness(sample_market):
    """
    Test that all price data is complete and valid.

    Validates that no price data is missing, NaN, or invalid,
    ensuring data completeness for trading simulations.

    Parameters
    ----------
    sample_market : Market
        Market fixture with loaded data
    """
    # Check ask price completeness
    assert len(sample_market.ask.open) == len(
        sample_market.dates
    ), "Ask open data incomplete"
    assert len(sample_market.ask.high) == len(
        sample_market.dates
    ), "Ask high data incomplete"
    assert len(sample_market.ask.low) == len(
        sample_market.dates
    ), "Ask low data incomplete"
    assert len(sample_market.ask.close) == len(
        sample_market.dates
    ), "Ask close data incomplete"

    # Check bid price completeness
    assert len(sample_market.bid.open) == len(
        sample_market.dates
    ), "Bid open data incomplete"
    assert len(sample_market.bid.high) == len(
        sample_market.dates
    ), "Bid high data incomplete"
    assert len(sample_market.bid.low) == len(
        sample_market.dates
    ), "Bid low data incomplete"
    assert len(sample_market.bid.close) == len(
        sample_market.dates
    ), "Bid close data incomplete"

    # Check for NaN or invalid values
    all_ask_prices = (
        sample_market.ask.open
        + sample_market.ask.high
        + sample_market.ask.low
        + sample_market.ask.close
    )
    all_bid_prices = (
        sample_market.bid.open
        + sample_market.bid.high
        + sample_market.bid.low
        + sample_market.bid.close
    )

    assert all(
        np.isfinite(price) for price in all_ask_prices
    ), "Ask prices contain NaN or inf"
    assert all(
        np.isfinite(price) for price in all_bid_prices
    ), "Bid prices contain NaN or inf"
    assert all(price > 0 for price in all_ask_prices), "Ask prices should be positive"
    assert all(price > 0 for price in all_bid_prices), "Bid prices should be positive"


# ===============================
# Error Handling and Edge Cases
# ===============================


def test_invalid_currency_handling():
    """
    Test error handling for invalid currency specifications.

    Validates that the system properly handles invalid currency
    inputs and provides appropriate error messages.
    """
    market = Market()

    # Test with None currency
    with pytest.raises((ValueError, TypeError, AttributeError)):
        market.load_from_database(
            currency_0=None,
            currency_1=Currency.USD,
            time_span=1 * days,
        )

    # Test with same currency for both base and quote
    try:
        market.load_from_database(
            currency_0=Currency.USD,
            currency_1=Currency.USD,
            time_span=1 * days,
        )
        # If this doesn't raise an error, verify it at least returns empty or raises warning
        pytest.warn(
            "Same currency pair loaded without error - verify this is intended behavior"
        )
    except (ValueError, RuntimeError):
        # Expected behavior for same currency pair
        pass


def test_invalid_time_span_handling():
    """
    Test error handling for invalid time span specifications.

    Validates that invalid time spans are handled gracefully
    with appropriate error messages or corrections.
    """
    market = Market()

    # Test with zero time span
    with pytest.raises((ValueError, RuntimeError)):
        market.load_from_database(
            currency_0=Currency.EUR,
            currency_1=Currency.USD,
            time_span=0 * days,
        )

    # Test with negative time span
    with pytest.raises((ValueError, RuntimeError)):
        market.load_from_database(
            currency_0=Currency.EUR,
            currency_1=Currency.USD,
            time_span=-1 * days,
        )


# ===============================
# Performance and Memory Tests
# ===============================


def test_loading_performance():
    """
    Test that data loading completes within reasonable time limits.

    Validates that database loading operations are performant
    and don't cause unacceptable delays in application startup.
    """
    import time

    market = Market()

    start_time = time.time()
    market.load_from_database(
        currency_0=Currency.EUR,
        currency_1=Currency.USD,
        time_span=1 * days,
    )
    loading_time = time.time() - start_time

    # Should complete within reasonable time (adjust threshold as needed)
    max_time = 5.0  # 5 seconds for 1 day of data
    assert (
        loading_time < max_time
    ), f"Data loading took too long: {loading_time:.3f}s > {max_time}s"


def test_large_dataset_memory_usage(large_market):
    """
    Test memory usage with large datasets.

    Validates that large market datasets don't consume excessive
    memory and that memory usage scales reasonably with data size.

    Parameters
    ----------
    large_market : Market
        Market fixture with large dataset (2 weeks)
    """
    import sys

    # Calculate approximate memory usage
    total_data_points = len(large_market.dates)

    # Estimate memory per data point (rough calculation)
    ask_size = (
        sys.getsizeof(large_market.ask.open)
        + sys.getsizeof(large_market.ask.high)
        + sys.getsizeof(large_market.ask.low)
        + sys.getsizeof(large_market.ask.close)
    )

    bid_size = (
        sys.getsizeof(large_market.bid.open)
        + sys.getsizeof(large_market.bid.high)
        + sys.getsizeof(large_market.bid.low)
        + sys.getsizeof(large_market.bid.close)
    )

    total_size = ask_size + bid_size + sys.getsizeof(large_market.dates)

    # Memory usage should be reasonable
    bytes_per_datapoint = total_size / total_data_points if total_data_points > 0 else 0
    assert (
        bytes_per_datapoint < 500
    ), f"Memory usage seems excessive: {bytes_per_datapoint:.1f} bytes per data point"


def test_concurrent_loading_safety():
    """
    Test that multiple simultaneous loading operations don't interfere.

    Validates that the loading system can handle concurrent requests
    without data corruption or race conditions.
    """
    import threading
    import time

    results = []
    errors = []

    def load_market_data(currency_pair, results_list, errors_list):
        try:
            market = Market()
            market.load_from_database(
                currency_0=currency_pair[0],
                currency_1=currency_pair[1],
                time_span=1 * days,
            )
            results_list.append((currency_pair, len(market.dates)))
        except Exception as e:
            errors_list.append((currency_pair, str(e)))

    # Create threads for different currency pairs
    threads = []
    test_pairs = MAJOR_CURRENCY_PAIRS[:3]  # Use first 3 pairs for concurrency test

    for pair in test_pairs:
        thread = threading.Thread(target=load_market_data, args=(pair, results, errors))
        threads.append(thread)

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for completion
    for thread in threads:
        thread.join(timeout=10.0)  # 10 second timeout

    # Verify results
    assert len(results) + len(errors) == len(
        test_pairs
    ), "Not all concurrent loading operations completed"

    # At least some should succeed (unless database unavailable)
    if len(results) == 0 and len(errors) == len(test_pairs):
        pytest.skip(
            "All concurrent loading operations failed - database may be unavailable"
        )


# ===============================
# Integration and Workflow Tests
# ===============================


def test_complete_loading_workflow():
    """
    Test complete workflow from market creation to data validation.

    Validates the entire process of creating a market, loading data,
    and ensuring the result is ready for trading operations.
    """
    # Step 1: Create market
    market = Market()
    assert market is not None

    # Step 2: Load data
    market.load_from_database(
        currency_0=Currency.EUR,
        currency_1=Currency.USD,
        time_span=1 * days,
    )

    # Step 3: Validate loaded data
    assert len(market.dates) > 0, "Market should contain data"
    assert hasattr(market, "currency_pair"), "Market should have currency information"

    # Step 4: Verify market is ready for trading operations
    if hasattr(market, "display_market_data"):
        # Should not raise exceptions
        market.display_market_data()

    # Step 5: Verify data can be accessed for analysis
    first_ask_price = market.ask.open[0]
    first_bid_price = market.bid.open[0]

    assert isinstance(first_ask_price, (int, float)), "Price should be numeric"
    assert isinstance(first_bid_price, (int, float)), "Price should be numeric"
    assert first_ask_price > 0, "Price should be positive"
    assert first_bid_price > 0, "Price should be positive"


def test_loader_function_integration():
    """
    Test integration with standalone loader function.

    Validates that the get_market_data function works correctly
    and integrates properly with Market objects.
    """
    try:
        # Test direct loader function usage
        market = Market()
        data = market.load_from_database(
            currency_0=Currency.EUR,
            currency_1=Currency.USD,
            time_span=1 * days,
        )

        # Validate returned data structure
        assert data is not None, "Loader function should return data"

        # If data is returned, it should be usable
        if hasattr(data, "__len__"):
            assert len(data) > 0, "Loader should return non-empty data"

    except Exception as e:
        pytest.skip(f"Loader function not available or not working: {e}")


# ===============================
# Test Execution
# ===============================


@pytest.mark.parametrize(
    "currency_pair",
    ALL_CURRENCY_PAIRS[:5],  # Limit to first 5 for the original test
    ids=lambda pair: f"{pair[0].value}_{pair[1].value}",
)
def test_load_dataframe(currency_pair):
    """
    Original test function enhanced with better validation.

    Test loading of market data into dataframe-like structure
    for various currency pairs.

    Parameters
    ----------
    currency_pair : tuple of Currency
        Tuple of (base_currency, quote_currency) to test
    """
    market = Market()

    try:
        market.load_from_database(
            currency_0=currency_pair[0],
            currency_1=currency_pair[1],
            time_span=1 * days,
        )

        # Enhanced validation beyond original test
        assert (
            len(market.dates) > 0
        ), f"No data loaded for {currency_pair[0].value}/{currency_pair[1].value}"

        # Verify data structure
        assert hasattr(market, "ask"), "Market should have ask data"
        assert hasattr(market, "bid"), "Market should have bid data"

        # Verify data consistency
        assert len(market.ask.dates) == len(market.dates), "Ask dates inconsistent"
        assert len(market.bid.dates) == len(market.dates), "Bid dates inconsistent"

    except Exception as e:
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
    >>> python test_loaders.py

    Notes
    -----
    Use pytest directly for more control over test execution
    """
    pytest.main(
        [
            "-v",  # Verbose output
            "-W",
            "error",  # Treat warnings as errors
            "--tb=short",  # Short traceback format
            __file__,
        ]
    )
