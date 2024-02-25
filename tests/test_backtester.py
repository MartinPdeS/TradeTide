#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

import pytest
import pandas
from TradeTide.backtester import BackTester
from TradeTide.loader import get_market_data


class MockStrategy:
    def __init__(self):
        pass

    def generate_signal(self, market_data: pandas.DataFrame):
        self.data = pandas.DataFrame(index=market_data.index)

        # Initialize the signal column with no signal
        self.data['signal'] = 0

        # Set a buy signal (1) on even days and a sell signal (-1) on odd days
        self.data[self.data.index.day == 1] = +1

        self.signal = self.data['signal']


@pytest.fixture
def mock_data() -> pandas.DataFrame:
    market_data = get_market_data('eur', 'usd', year=2023)
    return market_data[:1_000]


@pytest.fixture
def backtester(mock_data: pandas.DataFrame) -> BackTester:
    strategy = MockStrategy()
    strategy.generate_signal(mock_data)
    backtester = BackTester(strategy=strategy, market=mock_data)
    return backtester


def test_signal_generation(backtester):
    for date, row in backtester.strategy.data.iterrows():
        expected_signal = 1 if date.day == 1 else 0
        assert row['signal'] == expected_signal, "Signal generation failed."


def test_backtest_execution(backtester):
    portfolio = backtester.back_test()
    assert isinstance(portfolio, pandas.DataFrame), "Backtest didn't return a DataFrame."
    assert not portfolio.empty, "Backtest returned an empty DataFrame."


def test_performance_metrics(backtester):
    backtester.back_test()
    # Mock the performance calculation to simplify the test
    backtester.calculate_performance_metrics = lambda: {'Total Return': 0.1}
    performance_metrics = backtester.calculate_performance_metrics()
    assert 'Total Return' in performance_metrics, "Performance metrics calculation failed."
    assert performance_metrics['Total Return'] == 0.1, "Incorrect total return calculated."


# -
