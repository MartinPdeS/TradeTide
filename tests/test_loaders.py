#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from TradeTide.loader import get_market_data
from TradeTide.currencies import Currency
import pytest
from TradeTide.market import Market
from TradeTide.times import days
import TradeTide
TradeTide.debug_mode = True  # Enable debug mode for development purpose

currency_pairs = [
    (Currency.EUR, Currency.USD),
    (Currency.CHF, Currency.USD),
    (Currency.USD, Currency.GBP),
    (Currency.JPY, Currency.USD),
    (Currency.CAD, Currency.USD),
]


@pytest.mark.parametrize("currency_pair", currency_pairs, ids=lambda pair: f"{pair[0].value}_{pair[1].value}")
def test_load_dataframe(currency_pair: tuple) -> None:

    market = Market()
    market.load_from_database(
        currency_0=currency_pair[0],
        currency_1=currency_pair[1],
        time_span=1 * days,
    )

if __name__ == "__main__":
    pytest.main(["-W error", __file__])