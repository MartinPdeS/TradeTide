from TradeTide.market import Market
from TradeTide.portfolio import Portfolio
from TradeTide.position_collection import PositionCollection
from TradeTide.currencies import Currency
from datetime import timedelta
from TradeTide.signal import Signal
from TradeTide import capital_management, exit_strategy




market = Market()

time_span = timedelta(days=300)

market.load_from_database(
    currency_0=Currency.CAD,
    currency_1=Currency.USD,
    year=2023,
    time_span=time_span,
)

signal = Signal(market=market)

signal.generate_random(probability=0.01)

exit_strategy = exit_strategy.Static(
    stop_loss=4,
    take_profit=4,
    save_price_data=True
)


import time

start_time = time.time()


position_collection = PositionCollection(
    market=market,
    trade_signal=signal.trade_signal,
)

position_collection.open_positions(exit_strategy=exit_strategy)
position_collection.propagate_positions()

capital_management = capital_management.FixedLot(
    capital=1000000,
    fixed_lot_size=10000,
    max_capital_at_risk=100000,
    max_concurrent_positions=110,
)

portfolio  = Portfolio(
    position_collection=position_collection,
)

portfolio.simulate(capital_management=capital_management)

metrics = portfolio.get_metrics()
metrics.display()

end_time = time.time()
print(f"\nElapsed time: {end_time - start_time:.4f} seconds")




# portfolio.display()
# portfolio.plot_equity()
# portfolio.plot("equity", "capital", "number_of_positions")
# portfolio.plot(show=True)
# portfolio.plot_positions()

# portfolio.plot_positions(max_positions=300, show=True)
