import pytest
from datetime import timedelta
from TradeTide.market import Market
from TradeTide.signal import Signal
from TradeTide.position_collection import PositionCollection
from TradeTide import capital_management, exit_strategy
from TradeTide.portfolio import Portfolio
from TradeTide.currencies import Currency


@pytest.fixture
def setup_market():
    market = Market()
    market.load_from_database(
        currency_0=Currency.CAD,
        currency_1=Currency.USD,
        year=2023,
        time_span=timedelta(hours=2),
        spread_override=1,
        is_bid_override=True
    )
    return market


@pytest.fixture
def setup_signal(setup_market):
    signal = Signal(market=setup_market)
    signal.generate_random(probability=0.2)
    return signal


@pytest.fixture
def setup_exit_strategy():
    return exit_strategy.Trailing(stop_loss=10, take_profit=10, save_price_data=True)


def test_no_capital_means_no_trades(setup_market, setup_signal, setup_exit_strategy):
    position_collection = PositionCollection(
        market=setup_market,
        trade_signal=setup_signal.trade_signal,
        exit_strategy=setup_exit_strategy
    )
    position_collection.open_positions()
    position_collection.propagate_positions()

    risk = capital_management.FixedFractional(
        capital=0.0,  # no capital
        risk_per_trade=0.1,
        max_lot_size=1,
        max_capital_at_risk=100000,
        max_concurrent_positions=10,
    )

    portfolio = Portfolio(capital_management=risk, position_collection=position_collection)
    portfolio.simulate()

    assert len(portfolio.get_positions()) == 0
    assert portfolio.final_equity() == 0.0


def test_zero_signal_means_no_trades(setup_market, setup_exit_strategy):
    signal = Signal(setup_market)
    # All zeros by default
    position_collection = PositionCollection(
        market=setup_market,
        trade_signal=signal.trade_signal,
        exit_strategy=setup_exit_strategy
    )
    position_collection.open_positions()
    position_collection.propagate_positions()

    risk = capital_management.FixedFractional(
        capital=100000,
        risk_per_trade=0.05,
        max_lot_size=1,
        max_capital_at_risk=100000,
        max_concurrent_positions=10,
    )

    portfolio = Portfolio(capital_management=risk, position_collection=position_collection)
    portfolio.simulate()

    assert len(portfolio.get_positions()) == 0


def test_max_concurrent_positions_enforced(setup_market, setup_signal, setup_exit_strategy):
    position_collection = PositionCollection(
        market=setup_market,
        trade_signal=setup_signal.trade_signal,
        exit_strategy=setup_exit_strategy
    )
    position_collection.open_positions()
    position_collection.propagate_positions()

    risk = capital_management.FixedFractional(
        capital=100000,
        risk_per_trade=0.01,
        max_lot_size=2,
        max_capital_at_risk=100000,
        max_concurrent_positions=1,  # allow only 1 concurrent
    )

    portfolio = Portfolio(capital_management=risk, position_collection=position_collection)
    portfolio.simulate()

    open_counts = portfolio.open_position_history
    assert max(open_counts) <= 1


def test_risk_per_trade_zero_blocks_all_trades(setup_market, setup_signal, setup_exit_strategy):
    position_collection = PositionCollection(
        market=setup_market,
        trade_signal=setup_signal.trade_signal,
        exit_strategy=setup_exit_strategy
    )
    position_collection.open_positions()
    position_collection.propagate_positions()

    risk = capital_management.FixedFractional(
        capital=100000,
        risk_per_trade=0.0,  # no risk allowed
        max_lot_size=1,
        max_capital_at_risk=100000,
        max_concurrent_positions=10,
    )

    portfolio = Portfolio(capital_management=risk, position_collection=position_collection)
    portfolio.simulate()

    assert len(portfolio.get_positions()) == 0

if __name__ == "__main__":
    pytest.main(["-W error", __file__])