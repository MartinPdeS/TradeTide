from TradeTide.binary.interface_market import Market
from TradeTide.binary.interface_signal import Signal
from TradeTide.binary.interface_risk_managment import RiskManagment
from TradeTide.binary import interface_position_collection
from TradeTide.loader import get_data_path

from datetime import datetime, timedelta
import matplotlib.pyplot as plt

market = Market("usd/cad")


now = datetime.now()
tomorrow = now + timedelta(days=1)
interval = timedelta(minutes=1)


filename = get_data_path('cad', 'usd', year=2023)

market.load_from_csv(
    filename=str(filename) + '.csv',
    time_span=timedelta(hours=3),
)

signal = Signal(market=market)


signal.generate_random()

signal.display_signal()



risk_managment = RiskManagment(
    initial_balance=1000,
    risk_per_trade=10,
    stop_loss=10,
    take_profit=10
)



class PositionCollection(interface_position_collection.PositionCollection):
    pass


    def plot(self, figsize: tuple = (12, 4)) -> None:
        figure, ax = plt.subplots(1, 1, figsize=figsize)
        ax.plot(self.market.close_prices)

        plt.show()

position_collection = PositionCollection(
    market=market,
    signal=signal,
    risk_managment=risk_managment
)

position_collection.open_positions()

position_collection.close_positions()

position_collection.plot()

# position_collection.display()