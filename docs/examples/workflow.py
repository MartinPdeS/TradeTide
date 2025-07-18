"""
Trading Workflow Example
------------------------

This example demonstrates a complete trading workflow using the TradeTide library.

"""


from TradeTide import Strategy, Portfolio, PositionCollection, Market, Currency, days, hours, minutes
from TradeTide.indicators import BollingerBands
from TradeTide import capital_management, exit_strategy

market = Market()

market.load_from_database(
    currency_0=Currency.CAD,
    currency_1=Currency.USD,
    time_span=4 * hours,
)

# market.display()


indicator = BollingerBands(
    window=3 * minutes,
    multiplier=2.0
)

indicator.run(market)

strategy = Strategy()

strategy.add_indicator(indicator)

indicator.plot(show_bid=False)

exit_strategy = exit_strategy.Static(
    stop_loss=4,
    take_profit=4,
    save_price_data=True
)

position_collection = PositionCollection(
    market=market,
    trade_signal=strategy.get_trade_signal(market),
)

position_collection.open_positions(exit_strategy=exit_strategy)

position_collection.propagate_positions()

capital_management = capital_management.FixedLot(
    capital=1_000_000,
    fixed_lot_size=10_000,
    max_capital_at_risk=100_000,
    max_concurrent_positions=100,
)

portfolio  = Portfolio(position_collection=position_collection, debug_mode=False)

portfolio.simulate(capital_management=capital_management)

metrics = portfolio.get_metrics()

metrics.display()