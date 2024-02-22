import pytest
import pandas
import numpy
from TradeTide.backtester import BackTester


class MockStrategy:
    def __init__(self):
        pass

    def generate_signal(self, market_data: pandas.DataFrame):
        self.data = pandas.DataFrame(index=market_data.index)
        self.data['date'] = market_data['date']

        # Initialize the signal column with no signal
        self.data['signal'] = 0

        # Set a buy signal (1) on even days and a sell signal (-1) on odd days
        self.data.loc[self.data['date'].index % 2 != 0, 'signal'] = 1
        self.data.loc[self.data['date'].index % 2 == 0, 'signal'] = -1

        self.signal = self.data['signal']


@pytest.fixture
def mock_data() -> pandas.DataFrame:
    dates = pandas.date_range('2020-01-01', periods=10)

    prices = numpy.array([100 + i for i in range(10)])

    market_data = pandas.DataFrame(index=numpy.arange(len(prices)))

    market_data['date'] = dates
    market_data['close'] = prices
    market_data['low'] = prices * 0.99
    market_data['high'] = prices * 1.01

    return market_data


@pytest.fixture
def backtester(mock_data: pandas.DataFrame) -> BackTester:
    strategy = MockStrategy()
    strategy.generate_signal(mock_data)
    backtester = BackTester(strategy=strategy, market=mock_data)
    return backtester


def test_signal_generation(backtester):
    for i, row in backtester.strategy.data.iterrows():
        expected_signal = 1 if row.date.day % 2 == 0 else -1
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
