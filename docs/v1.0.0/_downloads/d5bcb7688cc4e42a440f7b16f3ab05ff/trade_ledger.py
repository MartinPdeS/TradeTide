"""
Trade Ledger and Position Analytics
===================================

Every ``BacktestResult`` includes a trade ledger.  Each row records costs,
holding time, exit classification, maximum adverse excursion (MAE), and maximum
favorable excursion (MFE), while the ledger provides portfolio-level position
analytics such as expectancy and streaks.
"""

# %%
# Create a short deterministic market and a single long signal.  Its compact
# price path makes the resulting holding time, MAE, and MFE easy to audit.

from datetime import datetime, timedelta

import numpy as np

from TradeTide import (
    Market,
    Portfolio,
    PositionCollection,
    capital_management,
    exit_strategy,
)
from TradeTide.execution import ExecutionCosts
from TradeTide.performance import BacktestResult

market = Market()
start = datetime(2024, 1, 1, 9)
market.add_market_data(
    start, 1.2002, 1.2004, 1.2000, 1.2002, 1.2000, 1.2002, 1.1998, 1.2000
)
market.add_market_data(
    start + timedelta(minutes=1),
    1.2004,
    1.2008,
    1.2002,
    1.2006,
    1.2002,
    1.2006,
    1.2000,
    1.2004,
)
market.add_market_data(
    start + timedelta(minutes=2),
    1.2006,
    1.2008,
    1.2004,
    1.2006,
    1.2004,
    1.2006,
    1.2002,
    1.2004,
)

positions = PositionCollection(market, np.array([1, 0, 0]))
positions.open_positions(exit_strategy.Static(stop_loss=2, take_profit=2))
positions.propagate_positions()

portfolio = Portfolio(positions)
portfolio.simulate(
    capital_management.FixedLot(
        capital=10_000,
        fixed_lot_size=100,
        max_capital_at_risk=1_000,
        max_concurrent_positions=1,
    )
)

# %%
# Add optional execution costs and inspect the ledger.  ``to_dataframe`` is
# convenient for notebooks and CSV/HTML reporting workflows.

result = BacktestResult.from_portfolio(
    portfolio,
    ExecutionCosts(commission_per_lot=0.001, slippage_pips=0.0),
)

print(result.ledger.to_dataframe())
print(result.ledger.analytics)
