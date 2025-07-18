"""
Backtester Workflow Example
---------------------------

This example demonstrates a complete backtesting workflow using the TradeTide library.

"""


from TradeTide import Backtester, Strategy, Market, Currency, days, hours, minutes
from TradeTide.indicators import BollingerBands
from TradeTide import capital_management, exit_strategy

market = Market()

market.load_from_database(
    currency_0=Currency.CAD,
    currency_1=Currency.USD,
    time_span=100 * days,
)

indicator = BollingerBands(
    window=3 * minutes,
    multiplier=2.0
)

indicator.run(market)

strategy = Strategy()

strategy.add_indicator(indicator)

exit_strategy = exit_strategy.Static(
    stop_loss=4,
    take_profit=4,
    save_price_data=True
)

capital_management = capital_management.FixedLot(
    capital=1_000_000,
    fixed_lot_size=10_000,
    max_capital_at_risk=100_000,
    max_concurrent_positions=100,
)

backtester = Backtester(
    strategy=strategy,
    exit_strategy=exit_strategy,
    market=market,
    capital_management=capital_management,
)

backtester.run()

backtester.print_performance()