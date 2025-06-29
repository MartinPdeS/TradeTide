"""
Unit tests for capital and position constraints in the TradeTide portfolio simulation.

These tests validate that risk management rules such as capital limits,
concurrent position caps, and trade signal filtering are enforced correctly.
"""

import pytest
from datetime import timedelta

from TradeTide.market import Market
from TradeTide.signal import Signal
from TradeTide.position_collection import PositionCollection
from TradeTide import capital_management, exit_strategy
from TradeTide.portfolio import Portfolio
from TradeTide.currencies import Currency
import TradeTide
TradeTide.debug_mode = True  # Enable debug mode for development purpose


# ------------------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------------------

@pytest.fixture
def setup_market():
    """Fixture to load a small slice of market data."""
    market = Market()
    market.load_from_database(
        currency_0=Currency.CAD,
        currency_1=Currency.USD,
        time_span=timedelta(hours=2),
    )
    return market


@pytest.fixture
def setup_signal(setup_market):
    """Fixture to generate random signals on the loaded market."""
    signal = Signal(market=setup_market)
    signal.generate_random(probability=0.2)
    return signal


@pytest.fixture
def strategy():
    """Fixture for a basic trailing stop-loss/take-profit strategy."""
    return exit_strategy.Trailing(stop_loss=10, take_profit=10, save_price_data=True)


# ------------------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------------------

def test_no_capital_means_no_trades(setup_market, setup_signal, strategy):
    """
    If max_concurrent_positions is 0, no positions should be opened
    regardless of trade signals or capital amount.
    """
    position_collection = PositionCollection(
        market=setup_market,
        trade_signal=setup_signal.trade_signal,
    )
    position_collection.open_positions(exit_strategy=strategy)
    position_collection.propagate_positions()

    capital_manager = capital_management.FixedLot(
        capital=1_000_000,
        fixed_lot_size=10_000,
        max_capital_at_risk=100_000,
        max_concurrent_positions=0,  # no positions allowed
    )

    portfolio = Portfolio(position_collection=position_collection)
    portfolio.simulate(capital_management=capital_manager)

    assert len(portfolio.get_positions()) == 0
    assert portfolio.state.equity == 1_000_000


def test_zero_signal_means_no_trades(setup_market, strategy):
    """
    If the trade signal contains only zeros (i.e., no signals),
    the system must not open any positions.
    """
    signal = Signal(setup_market)  # All zeros by default
    position_collection = PositionCollection(
        market=setup_market,
        trade_signal=signal.trade_signal,
    )
    position_collection.open_positions(exit_strategy=strategy)
    position_collection.propagate_positions()

    capital_manager = capital_management.FixedFractional(
        capital=100_000,
        risk_per_trade=0.05,
        max_capital_at_risk=100_000,
        max_concurrent_positions=10,
    )

    portfolio = Portfolio(position_collection=position_collection)
    portfolio.simulate(capital_management=capital_manager)

    assert len(portfolio.get_positions()) == 0


def test_max_concurrent_positions_enforced(setup_market, setup_signal, strategy):
    """
    The portfolio must not exceed the defined max_concurrent_positions limit.
    """
    position_collection = PositionCollection(
        market=setup_market,
        trade_signal=setup_signal.trade_signal,
    )
    position_collection.open_positions(exit_strategy=strategy)
    position_collection.propagate_positions()

    capital_manager = capital_management.FixedFractional(
        capital=100_000,
        risk_per_trade=0.01,
        max_capital_at_risk=100_000,
        max_concurrent_positions=1,  # enforce strict limit
    )

    portfolio = Portfolio(position_collection=position_collection)
    portfolio.simulate(capital_management=capital_manager)

    assert max(portfolio.record.concurrent_positions) <= 1


def test_risk_per_trade_zero_blocks_all_trades(setup_market, setup_signal, strategy):
    """
    If risk_per_trade is zero, no trades should be executed.
    """
    position_collection = PositionCollection(
        market=setup_market,
        trade_signal=setup_signal.trade_signal,
    )
    position_collection.open_positions(exit_strategy=strategy)
    position_collection.propagate_positions()

    capital_manager = capital_management.FixedFractional(
        capital=100_000,
        risk_per_trade=0.0,  # zero risk => no trades
        max_capital_at_risk=100_000,
        max_concurrent_positions=10,
    )

    portfolio = Portfolio(position_collection=position_collection)
    portfolio.simulate(capital_management=capital_manager)

    assert len(portfolio.get_positions()) == 0


# ------------------------------------------------------------------------------
# Run directly (optional)
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main(["-W", "error", __file__])
