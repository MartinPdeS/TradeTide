from TradeTide.indicators import BollingerBands
from TradeTide.market import Market
from TradeTide.currencies import Currency
from TradeTide.times import days, minutes
from TradeTide.market import Market
from TradeTide.currencies import Currency
from TradeTide import capital_management, exit_strategy
from TradeTide.position_collection import PositionCollection
from TradeTide.portfolio import Portfolio

market = Market()

market.load_from_database(
    currency_0=Currency.CAD,
    currency_1=Currency.USD,
    time_span=300 * days,
)

indicator = BollingerBands(
    window=3 * minutes,
    multiplier=2.0
)

indicator.run(market)

exit_strategy = exit_strategy.Static(
    stop_loss=4,
    take_profit=4,
    save_price_data=True
)

position_collection = PositionCollection(
    market=market,
    trade_signal=indicator._cpp_signals,
)

position_collection.open_positions(exit_strategy=exit_strategy)

position_collection.propagate_positions()

capital_management = capital_management.FixedLot(
    capital=1000000,
    fixed_lot_size=10000,
    max_capital_at_risk=100000,
    max_concurrent_positions=110,
)

portfolio  = Portfolio(position_collection=position_collection)

portfolio.simulate(capital_management=capital_management)

metrics = portfolio.get_metrics()

metrics.display()