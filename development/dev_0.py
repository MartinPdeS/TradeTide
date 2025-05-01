from TradeTide.binary.interface_market import Market
from TradeTide.binary.interface_signal import Signal
from TradeTide.binary.interface_risk_managment import RiskManagment
from TradeTide.binary.interface_position_collection import PositionCollection

from datetime import datetime, timedelta


market = Market("usd/cad")


now = datetime.now()
tomorrow = now + timedelta(days=1)
interval = timedelta(hours=1)


market.generate_random_market_data(
    start=now,
    end=tomorrow,
    interval=interval
)

# market.display_market_data()

signal = Signal(market=market)


signal.generate_random()
#
signal.display_signal()
# dsa
# print(signal.trade_signal)


risk_managment = RiskManagment(
    initial_balance=1000,
    risk_per_trade=10,
    stop_loss=10,
    take_profit=10
)

position_collection = PositionCollection(
    market=market,
    signal=signal,
    risk_managment=risk_managment
)

position_collection.open_positions()

print('number_of_trade', position_collection.number_of_trade)


# position_collection.display()