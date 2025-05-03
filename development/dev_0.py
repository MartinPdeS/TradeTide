from TradeTide.market import Market
from TradeTide.binary.interface_signal import Signal
from TradeTide.binary.interface_risk_managment import RiskManagment
from TradeTide.loader import get_data_path
from MPSPlots.styles import mps
from TradeTide.position_collection import PositionCollection
from TradeTide.currencies import Currency
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

market = Market()


now = datetime.now()
tomorrow = now + timedelta(days=1)
interval = timedelta(minutes=1)


filename = get_data_path('cad', 'usd', year=2023)

market.load_from_database(
    currency_0=Currency.CAD,
    currency_1=Currency.USD,
    year=2023,
    time_span=timedelta(hours=3),
    spread_override=10,
    is_bid_override=True
)

# market.set_price_type(type="open", is_bid=False)

market.plot()

signal = Signal(market=market)


signal.generate_random(probability=0.03)

signal.display_signal()

risk_managment = RiskManagment(
    initial_balance=100,
    risk_per_trade=10,
    stop_loss=20,
    take_profit=20
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
