from TradeTide.binary.interface_market import Market
from TradeTide.binary.interface_signal import Signal
from TradeTide.binary.interface_risk_managment import RiskManagment
from TradeTide.loader import get_data_path
from MPSPlots.styles import mps
from TradeTide.position_collection import PositionCollection

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

print(market.spreads)

market.set_price_type(type="open", is_bid=False)

signal = Signal(market=market)


signal.generate_random(probability=0.03)

signal.display_signal()

risk_managment = RiskManagment(
    initial_balance=100,
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

position_collection.close_positions()

position_collection.terminate_open_positions()

position_collection.display()
position_collection.plot()
