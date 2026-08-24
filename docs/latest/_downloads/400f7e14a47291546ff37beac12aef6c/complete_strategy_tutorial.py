"""
Build a Complete Strategy
=========================

This end-to-end tutorial follows the complete TradeTide workflow: load and
validate data, calculate an indicator, turn its signals into orders, simulate a
portfolio, inspect the trade ledger, and plot net equity and drawdown.  It uses
bundled EUR/USD data and is intended as a reproducible research example, not
investment advice.
"""

# %%
# Imports and diagnostics
# -----------------------
#
# Logging is opt-in.  DEBUG logs explain order fills, validation results, costs,
# and calculated metrics.  Use ``enable_debug_logging()`` instead when native
# position and portfolio diagnostics are also required.

import logging

from TradeTide import (
    Currency,
    Market,
    Order,
    OrderBook,
    OrderSide,
    OrderType,
    Portfolio,
    PositionCollection,
    Strategy,
    configure_logging,
    validate_market_data,
)
from TradeTide import capital_management, exit_strategy
from TradeTide.execution import ExecutionCosts
from TradeTide.indicators import BollingerBands
from TradeTide.performance import BacktestResult
from TradeTide.times import hours, minutes

configure_logging(logging.DEBUG)

# %%
# Load and validate data
# ----------------------

market = Market()
market.load_from_database(Currency.EUR, Currency.USD, time_span=12 * hours)
quality = validate_market_data(market, max_spread_ratio=0.02)
quality.raise_for_errors()
print(f"Loaded {len(market.dates)} EUR/USD candles; warnings: {len(quality.warnings)}")

# %%
# Build an indicator and derive trade signals
# -------------------------------------------

strategy = Strategy()
strategy.add_indicator(BollingerBands(window=30 * minutes, multiplier=2.0))
raw_signals = strategy.get_trade_signal(market)

# %%
# Translate signals into executable market orders
# -----------------------------------------------
#
# The order book is also useful when a strategy instead creates limit, stop, or
# stop-limit orders.  Its fills form the exact signal stream supplied to native
# position management.

orders = [
    Order(
        order_id=f"signal-{index}",
        side=OrderSide.BUY if signal == 1 else OrderSide.SELL,
        order_type=OrderType.MARKET,
        submitted_at=market.dates[index],
    )
    for index, signal in enumerate(raw_signals)
    if signal in (-1, 1)
]
order_book = OrderBook(orders)
entry_signals = order_book.trade_signals(market)
print(f"Signals: {len(orders)}; fills: {len(order_book.fills)}")

# %%
# Simulate positions and a portfolio
# ----------------------------------

positions = PositionCollection(market, entry_signals)
positions.open_positions(exit_strategy.Static(stop_loss=4, take_profit=4))
positions.propagate_positions()

portfolio = Portfolio(positions)
portfolio.simulate(
    capital_management.FixedLot(
        capital=100_000,
        fixed_lot_size=10_000,
        max_capital_at_risk=10_000,
        max_concurrent_positions=1,
    )
)

# %%
# Inspect the ledger and risk-adjusted metrics
# --------------------------------------------

result = BacktestResult.from_portfolio(
    portfolio,
    ExecutionCosts(commission_per_lot=0.0001, slippage_pips=0.05),
)
print(result.metrics.to_dict())
print(result.ledger.to_dataframe().head())

# %%
# Plot equity candles and drawdown
# --------------------------------

result.plot_equity_drawdown(max_candles=300)
