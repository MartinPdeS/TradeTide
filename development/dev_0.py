from TradeTide.market import Market
from TradeTide.portfolio import Portfolio
from TradeTide.position_collection import PositionCollection
from TradeTide.currencies import Currency
from datetime import timedelta
from TradeTide.signal import Signal
from TradeTide import capital_management, exit_strategy

market = Market()


market.load_from_database(
    currency_0=Currency.CAD,
    currency_1=Currency.USD,
    year=2023,
    time_span=timedelta(hours=30),
)

signal = Signal(market=market)

signal.generate_random(probability=0.12)

exit_strategy = exit_strategy.Static(
    stop_loss=10,
    take_profit=10,
    save_price_data=True
)


position_collection = PositionCollection(
    market=market,
    trade_signal=signal.trade_signal,
)

position_collection.open_positions(exit_strategy=exit_strategy)
position_collection.propagate_positions()
position_collection.terminate_open_positions()

# position_collection.plot(max_positions=4)

capital_management = capital_management.FixedFractional(
    capital=1000000,
    risk_per_trade=0.001,
    max_capital_at_risk=10000000,
    max_concurrent_positions=6,
)

portfolio  = Portfolio(
    position_collection=position_collection,
    save_history=True
)

portfolio.simulate(capital_management=capital_management)

# portfolio.display()
# portfolio.plot_equity()
portfolio.plot(show=True)


# portfolio.plot_positions(max_positions=300, show=True)
