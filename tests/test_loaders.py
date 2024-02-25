#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from TradeTide.loader import get_market_data
import pytest

currency_pairs = [
    ('eur', 'usd'),
    ('chf', 'usd'),
    ('gpb', 'usd'),
    ('jpy', 'usd'),
    ('cad', 'usd'),
]


@pytest.mark.parametrize("currency_pair", currency_pairs)
def test_load_dataframe(currency_pair: tuple) -> None:
    data_frame = get_market_data('eur', 'usd', year=2023)

    print(data_frame.columns)

    data_frame = get_market_data('usd', 'eur', year=2023)

# -
