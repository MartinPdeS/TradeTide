"""
Interactive HTML Backtest Report
===============================

Create a portable Plotly report containing interactive equity, drawdown, trade
markers, performance metrics, and the complete ledger. Install the optional
reporting extra first: ``pip install 'TradeTide[reporting]'``.
"""

from TradeTide import BacktestResult, Market, Portfolio, PositionCollection
from TradeTide import Strategy, Currency, BollingerBands, capital_management, exit_strategy
from TradeTide.times import hours

market = Market()
market.load_from_database(Currency.CAD, Currency.USD, 4 * hours)

strategy = Strategy()
strategy.add_indicator(BollingerBands(window=20, multiplier=2.0))
signals = strategy.get_trade_signal(market)

positions = PositionCollection(market, signals)
positions.open_positions(exit_strategy.Static(stop_loss=4, take_profit=4))
positions.propagate_positions()

portfolio = Portfolio(positions)
portfolio.simulate(
    capital_management.FixedLot(
        capital=100_000,
        fixed_lot_size=1.0,
        max_capital_at_risk=5_000,
        max_concurrent_positions=3,
    )
)

result = BacktestResult.from_portfolio(portfolio)
report = result.to_html("reports/bollinger_backtest.html", open_browser=True)
print(f"Interactive report written to {report}")
