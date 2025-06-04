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

signal.generate_random(probability=0.001)

exit_strategy = exit_strategy.Static(
    stop_loss=4,
    take_profit=4,
    save_price_data=True
)


# Short Position:
# Start Time: 2024-02-22 00:59:00.000000
# Stop Time: 2024-02-22 00:59:00.000000
# Entry Price: 1.34873
# Exit Price: 1.34874
# Lot Size: 1.00000


import time

start_time = time.time()


position_collection = PositionCollection(
    market=market,
    trade_signal=signal.trade_signal,
)

position_collection.open_positions(exit_strategy=exit_strategy)
position_collection.propagate_positions()

# position_collection.display()

# position_collection.plot()


capital_management = capital_management.FixedLot(
    capital=1000000,
    fixed_lot_size=10000,
    max_capital_at_risk=100000,
    max_concurrent_positions=110,
)

portfolio  = Portfolio(
    position_collection=position_collection,
    save_history=True
)

portfolio.simulate(capital_management=capital_management)


# dsa

end_time = time.time()
print(f"\nElapsed time: {end_time - start_time:.4f} seconds")




# portfolio.display()
# portfolio.plot_equity()
portfolio.plot("equity", "capital", "number_of_positions")
# portfolio.plot(show=True)
# portfolio.plot_positions()

# portfolio.plot_positions(max_positions=300, show=True)
