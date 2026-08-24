from datetime import timedelta

import pytest

from TradeTide.currencies import Currency
from TradeTide.market import Market


def test_time_span_accepts_combined_duration_string():
    assert Market()._parse_timespan("1d 2h 30m") == timedelta(days=1, hours=2, minutes=30)


@pytest.mark.parametrize("value", [timedelta(), timedelta(seconds=-1), "0m", "-1h", "tomorrow"])
def test_time_span_must_be_a_positive_duration(value):
    with pytest.raises(ValueError, match="time_span"):
        Market()._parse_timespan(value)


def test_time_span_rejects_unrecognised_types():
    with pytest.raises(TypeError, match="datetime.timedelta"):
        Market()._parse_timespan(60)


def test_currency_pair_requires_currency_members():
    with pytest.raises(TypeError, match="currency_0"):
        Market().load_from_database("EUR", Currency.USD, timedelta(hours=1))


def test_currency_pair_requires_distinct_currencies():
    with pytest.raises(ValueError, match="must be different"):
        Market().load_from_database(Currency.USD, Currency.USD, timedelta(hours=1))


def test_missing_dataset_names_the_available_data():
    with pytest.raises(FileNotFoundError, match="Available datasets"):
        Market().load_from_database(Currency.AUD, Currency.NZD, timedelta(hours=1))
