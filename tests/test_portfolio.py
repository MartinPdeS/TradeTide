import pytest
from datetime import datetime, timedelta
from TradeTide.market import Market
from TradeTide.portfolio import Portfolio
from TradeTide.loader import get_data_path
from TradeTide.position_collection import PositionCollection
from TradeTide.currencies import Currency
from TradeTide.signal import Signal
from TradeTide import capital_management, exit_strategy


def test_portfolio_simulation_workflow():
    """Full end-to-end test of portfolio simulation with random signal."""

    # Setup market
    market = Market()
    market.load_from_database(
        currency_0=Currency.CAD,
        currency_1=Currency.USD,
        time_span=timedelta(hours=3),
    )
    assert len(market.dates) > 0, "Market data failed to load"

    # Generate signal
    signal = Signal(market=market)
    signal.generate_random(probability=0.12)
    assert len(signal.trade_signal) == len(market.dates), "Signal length mismatch"

    # Define exit strategy
    strategy = exit_strategy.Trailing(
        stop_loss=10,
        take_profit=10,
        save_price_data=True
    )

    # Open and propagate positions
    position_collection = PositionCollection(
        market=market,
        trade_signal=signal.trade_signal,
    )
    position_collection.open_positions(exit_strategy=strategy)
    position_collection.propagate_positions()

    assert len(position_collection) > 0, "No positions opened"

    # Define capital management
    capital_manager = capital_management.FixedFractional(
        capital=100000,
        risk_per_trade=0.01,
        max_capital_at_risk=100000,
        max_concurrent_positions=1,
    )

    # Build and simulate portfolio
    portfolio = Portfolio(position_collection=position_collection)

    portfolio.simulate(capital_management=capital_manager)

    # Assertions
    assert len(portfolio.get_positions()) > 0, "No positions selected"
    assert len(portfolio.record.equity) == len(market.dates), "Equity curve not computed correctly"
    assert all(e >= 0 for e in portfolio.record.equity), "Negative equity value found"

    # Optional: Run plotting for visual check (disable show=True for CI)
    portfolio.plot_positions(max_positions=100, show=False)

if __name__ == "__main__":
    pytest.main(["-W error", __file__])
