"""
Comprehensive test suite for TradeTide.currencies module.

This module tests the Currency enum functionality including:
- Currency code enumeration and validation
- Currency listing and membership testing
- Enum behavior and properties
- Edge cases and error handling

Tests follow pytest best practices with fixtures, parametrized tests,
and comprehensive coverage of enum functionality.
"""

import pytest
from enum import Enum

from TradeTide.currencies import Currency


# ------------------------------------------------------------------------------
# Test Fixtures
# ------------------------------------------------------------------------------

@pytest.fixture
def all_currency_codes():
    """
    Fixture providing all valid currency codes.

    Returns
    -------
    list of str
        List of all valid currency code strings
    """
    return [
        "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY",
        "NZD", "SEK", "MXN", "SGD", "HKD", "NOK", "KRW", "TRY",
        "INR", "RUB", "ZAR", "BRL"
    ]


@pytest.fixture
def major_currencies():
    """
    Fixture providing major currency pairs for trading.

    Returns
    -------
    list of Currency
        List of major Currency enum instances
    """
    return [Currency.USD, Currency.EUR, Currency.GBP, Currency.JPY]


@pytest.fixture
def sample_currency_pairs():
    """
    Fixture providing sample currency pairs for testing.

    Returns
    -------
    list of tuple
        List of (base_currency, quote_currency) tuples
    """
    return [
        (Currency.EUR, Currency.USD),
        (Currency.GBP, Currency.USD),
        (Currency.USD, Currency.JPY),
        (Currency.AUD, Currency.USD),
        (Currency.USD, Currency.CAD),
        (Currency.USD, Currency.CHF),
    ]


# ------------------------------------------------------------------------------
# Test Cases for Currency Enum Basic Functionality
# ------------------------------------------------------------------------------

class TestCurrencyBasics:
    """Test suite for basic Currency enum functionality."""

    def test_currency_enum_inheritance(self):
        """Test that Currency is properly inheriting from Enum."""
        assert issubclass(Currency, Enum)
        assert isinstance(Currency.USD, Currency)
        assert isinstance(Currency.EUR, Enum)

    @pytest.mark.parametrize("currency_code", [
        "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY",
        "NZD", "SEK", "MXN", "SGD", "HKD", "NOK", "KRW", "TRY",
        "INR", "RUB", "ZAR", "BRL"
    ])
    def test_currency_access_by_name(self, currency_code):
        """
        Test that currencies can be accessed by name.

        Parameters
        ----------
        currency_code : str
            Currency code to test
        """
        currency = getattr(Currency, currency_code)
        assert isinstance(currency, Currency)
        assert currency.value == currency_code

    @pytest.mark.parametrize("currency_code", [
        "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY",
        "NZD", "SEK", "MXN", "SGD", "HKD", "NOK", "KRW", "TRY",
        "INR", "RUB", "ZAR", "BRL"
    ])
    def test_currency_access_by_value(self, currency_code):
        """
        Test that currencies can be accessed by value.

        Parameters
        ----------
        currency_code : str
            Currency code to test
        """
        currency = Currency(currency_code)
        assert isinstance(currency, Currency)
        assert currency.value == currency_code

    def test_currency_string_representation(self):
        """Test string representation of Currency instances."""
        assert str(Currency.USD) == "Currency.USD"
        assert repr(Currency.EUR) == "<Currency.EUR: 'EUR'>"
        assert Currency.GBP.name == "GBP"
        assert Currency.JPY.value == "JPY"

    def test_currency_equality(self):
        """Test equality comparison between Currency instances."""
        # Same currency should be equal
        assert Currency.USD == Currency.USD
        assert Currency.EUR == Currency.EUR

        # Different currencies should not be equal
        assert Currency.USD != Currency.EUR
        assert Currency.GBP != Currency.JPY

        # Test with constructed instances
        usd1 = Currency("USD")
        usd2 = Currency("USD")
        eur1 = Currency("EUR")

        assert usd1 == usd2
        assert usd1 != eur1

    def test_currency_hashing(self):
        """Test that Currency instances are hashable and can be used as dict keys."""
        currency_dict = {
            Currency.USD: "US Dollar",
            Currency.EUR: "Euro",
            Currency.GBP: "British Pound"
        }

        assert currency_dict[Currency.USD] == "US Dollar"
        assert currency_dict[Currency.EUR] == "Euro"
        assert currency_dict[Currency.GBP] == "British Pound"

        # Test with constructed instance
        usd_key = Currency("USD")
        assert currency_dict[usd_key] == "US Dollar"

    def test_currency_in_set(self):
        """Test Currency instances in sets."""
        currency_set = {Currency.USD, Currency.EUR, Currency.GBP}

        assert Currency.USD in currency_set
        assert Currency.EUR in currency_set
        assert Currency.JPY not in currency_set

        # Test with constructed instance
        assert Currency("USD") in currency_set

    def test_currency_ordering_not_supported(self):
        """Test that Currency instances don't support ordering by default."""
        with pytest.raises(TypeError):
            Currency.USD < Currency.EUR  # Should raise TypeError

        with pytest.raises(TypeError):
            Currency.USD > Currency.GBP  # Should raise TypeError


# ------------------------------------------------------------------------------
# Test Cases for Currency List Method
# ------------------------------------------------------------------------------

class TestCurrencyListMethod:
    """Test suite for the Currency.list() class method."""

    def test_list_method_returns_all_currencies(self, all_currency_codes):
        """Test that list() method returns all currency codes."""
        currency_list = Currency.list()

        # Should return a list
        assert isinstance(currency_list, list)

        # Should contain all expected currencies
        assert set(currency_list) == set(all_currency_codes)

        # Should contain only strings
        assert all(isinstance(code, str) for code in currency_list)

    def test_list_method_length(self, all_currency_codes):
        """Test that list() method returns correct number of currencies."""
        currency_list = Currency.list()
        assert len(currency_list) == len(all_currency_codes)

    def test_list_method_no_duplicates(self):
        """Test that list() method returns no duplicate currency codes."""
        currency_list = Currency.list()
        assert len(currency_list) == len(set(currency_list))

    def test_list_method_consistency(self):
        """Test that list() method returns consistent results across calls."""
        list1 = Currency.list()
        list2 = Currency.list()

        # Should return the same currencies (order may vary in some implementations)
        assert set(list1) == set(list2)

    def test_list_method_immutability(self):
        """Test that modifying returned list doesn't affect the enum."""
        original_list = Currency.list()
        original_length = len(original_list)

        # Modify the returned list
        modified_list = Currency.list()
        modified_list.append("FAKE")

        # Original should be unchanged
        new_list = Currency.list()
        assert len(new_list) == original_length
        assert "FAKE" not in new_list

    @pytest.mark.parametrize("expected_currency", [
        "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY"
    ])
    def test_list_contains_major_currencies(self, expected_currency):
        """
        Test that list() method contains major world currencies.

        Parameters
        ----------
        expected_currency : str
            Currency code that should be in the list
        """
        currency_list = Currency.list()
        assert expected_currency in currency_list


# ------------------------------------------------------------------------------
# Test Cases for Currency Validation and Error Handling
# ------------------------------------------------------------------------------

class TestCurrencyValidation:
    """Test suite for Currency validation and error handling."""

    @pytest.mark.parametrize("invalid_code", [
        "INVALID",
        "XXX",
        "US",  # Too short
        "USDX",  # Too long
        "usd",  # Wrong case
        "123",  # Numbers
        "",  # Empty string
        " USD ",  # With spaces
        "US D",  # With space
        None,  # None value
    ])
    def test_invalid_currency_codes_raise_error(self, invalid_code):
        """
        Test that invalid currency codes raise ValueError.

        Parameters
        ----------
        invalid_code : str or None
            Invalid currency code that should raise an error
        """
        with pytest.raises((ValueError, KeyError, TypeError)):
            Currency(invalid_code)

    def test_accessing_nonexistent_attribute_raises_error(self):
        """Test that accessing non-existent currency raises AttributeError."""
        with pytest.raises(AttributeError):
            Currency.NONEXISTENT

    def test_case_sensitivity(self):
        """Test that currency codes are case-sensitive."""
        # Valid uppercase should work
        assert Currency("USD").value == "USD"

        # Invalid lowercase should fail
        with pytest.raises((ValueError, KeyError)):
            Currency("usd")

        # Mixed case should fail
        with pytest.raises((ValueError, KeyError)):
            Currency("Usd")


# ------------------------------------------------------------------------------
# Test Cases for Currency Practical Usage
# ------------------------------------------------------------------------------

class TestCurrencyPracticalUsage:
    """Test suite for practical usage scenarios."""

    def test_currency_pair_creation(self, sample_currency_pairs):
        """
        Test creating currency pairs for trading.

        Parameters
        ----------
        sample_currency_pairs : list
            List of (base, quote) currency pairs
        """
        for base, quote in sample_currency_pairs:
            assert isinstance(base, Currency)
            assert isinstance(quote, Currency)
            assert base != quote  # Base and quote should be different

            # Should be able to create pair identifier
            pair_id = f"{base.value}{quote.value}"
            assert len(pair_id) == 6  # Should be 6 characters (3+3)

    def test_currency_conversion_mapping(self, major_currencies):
        """
        Test creating conversion rate mapping.

        Parameters
        ----------
        major_currencies : list
            List of major Currency instances
        """
        conversion_rates = {}

        for base in major_currencies:
            for quote in major_currencies:
                if base != quote:
                    pair = (base, quote)
                    conversion_rates[pair] = 1.0  # Dummy rate

        # Should have rates for all pairs except self-pairs
        expected_pairs = len(major_currencies) * (len(major_currencies) - 1)
        assert len(conversion_rates) == expected_pairs

        # Test accessing rates
        if Currency.EUR in major_currencies and Currency.USD in major_currencies:
            assert (Currency.EUR, Currency.USD) in conversion_rates

    def test_currency_portfolio_allocation(self, all_currency_codes):
        """
        Test using currencies for portfolio allocation.

        Parameters
        ----------
        all_currency_codes : list
            List of all currency codes
        """
        # Create portfolio allocation
        portfolio = {}
        for i, code in enumerate(all_currency_codes[:5]):  # Use first 5 currencies
            currency = Currency(code)
            portfolio[currency] = (i + 1) * 1000  # Dummy allocation

        # Test portfolio operations
        total_allocation = sum(portfolio.values())
        assert total_allocation > 0

        # Test portfolio querying
        if Currency.USD in portfolio:
            usd_allocation = portfolio[Currency.USD]
            assert isinstance(usd_allocation, (int, float))

    def test_currency_filtering_and_grouping(self, all_currency_codes):
        """
        Test filtering and grouping currencies.

        Parameters
        ----------
        all_currency_codes : list
            List of all currency codes
        """
        # Group by regions (simplified example)
        european_codes = ["EUR", "GBP", "CHF", "SEK", "NOK"]
        asian_codes = ["JPY", "CNY", "KRW", "SGD", "HKD"]

        european_currencies = [Currency(code) for code in european_codes if code in all_currency_codes]
        asian_currencies = [Currency(code) for code in asian_codes if code in all_currency_codes]

        # Test that grouping works
        assert len(european_currencies) > 0
        assert len(asian_currencies) > 0

        # Test that currencies are distinct between groups
        european_set = set(european_currencies)
        asian_set = set(asian_currencies)
        assert len(european_set.intersection(asian_set)) == 0


# ------------------------------------------------------------------------------
# Test Cases for Currency Enum Completeness
# ------------------------------------------------------------------------------

class TestCurrencyCompleteness:
    """Test suite for ensuring Currency enum completeness."""

    def test_major_world_currencies_present(self):
        """Test that major world currencies are included."""
        major_currencies = [
            "USD",  # US Dollar
            "EUR",  # Euro
            "GBP",  # British Pound
            "JPY",  # Japanese Yen
            "AUD",  # Australian Dollar
            "CAD",  # Canadian Dollar
            "CHF",  # Swiss Franc
            "CNY",  # Chinese Yuan
        ]

        currency_list = Currency.list()

        for major in major_currencies:
            assert major in currency_list, f"Major currency {major} is missing"

    def test_emerging_market_currencies_present(self):
        """Test that important emerging market currencies are included."""
        emerging_currencies = [
            "BRL",  # Brazilian Real
            "INR",  # Indian Rupee
            "RUB",  # Russian Ruble
            "ZAR",  # South African Rand
            "MXN",  # Mexican Peso
            "TRY",  # Turkish Lira
        ]

        currency_list = Currency.list()

        for emerging in emerging_currencies:
            assert emerging in currency_list, f"Emerging currency {emerging} is missing"

    def test_all_currencies_three_letter_codes(self):
        """Test that all currencies follow ISO 4217 three-letter format."""
        currency_list = Currency.list()

        for code in currency_list:
            assert len(code) == 3, f"Currency code {code} is not 3 characters"
            assert code.isupper(), f"Currency code {code} is not uppercase"
            assert code.isalpha(), f"Currency code {code} contains non-alphabetic characters"

    def test_currency_enum_members_count(self):
        """Test that Currency enum has expected number of members."""
        # Should have at least 20 currencies (as defined in the source)
        assert len(list(Currency)) >= 20

        # Should match the list() method count
        assert len(list(Currency)) == len(Currency.list())


# ------------------------------------------------------------------------------
# Performance and Edge Case Tests
# ------------------------------------------------------------------------------

class TestCurrencyPerformanceAndEdgeCases:
    """Performance and edge case tests for Currency enum."""

    def test_currency_access_performance(self):
        """Test performance of currency access operations."""
        import time

        currency_codes = Currency.list()

        # Test enum member access performance
        start_time = time.time()
        for _ in range(1000):
            for code in currency_codes[:10]:  # Test with first 10 currencies
                currency = Currency(code)
                _ = currency.value
        end_time = time.time()

        # Should complete quickly
        assert end_time - start_time < 1.0, "Currency access too slow"

    def test_currency_list_performance(self):
        """Test performance of Currency.list() method."""
        import time

        start_time = time.time()
        for _ in range(1000):
            currency_list = Currency.list()
        end_time = time.time()

        # Should complete quickly
        assert end_time - start_time < 1.0, "Currency.list() too slow"

    def test_memory_usage_with_many_instances(self):
        """Test memory behavior with many Currency instances."""
        # Create many instances of the same currency
        currencies = [Currency.USD for _ in range(1000)]

        # All should be the same object (enum singleton behavior)
        first_currency = currencies[0]
        for currency in currencies:
            assert currency is first_currency, "Currency instances should be singletons"

    def test_currency_with_special_scenarios(self):
        """Test Currency behavior in special scenarios."""
        # Test enum iteration
        all_currencies = list(Currency)
        assert len(all_currencies) > 0

        # Test that all currencies in iteration are valid
        for currency in all_currencies:
            assert isinstance(currency, Currency)
            assert currency.value in Currency.list()

    def test_currency_pickle_serialization(self):
        """Test that Currency instances can be pickled/unpickled."""
        import pickle

        original = Currency.USD
        pickled = pickle.dumps(original)
        unpickled = pickle.loads(pickled)

        assert unpickled == original
        assert unpickled is original  # Should be the same object

    def test_currency_json_serialization_preparation(self):
        """Test preparing Currency for JSON serialization."""
        currency = Currency.EUR

        # Should be able to extract string value for JSON
        json_value = currency.value
        assert isinstance(json_value, str)
        assert json_value == "EUR"

        # Should be able to reconstruct from JSON value
        reconstructed = Currency(json_value)
        assert reconstructed == currency

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
