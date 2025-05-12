from TradeTide.market import Market
from TradeTide.binary.interface_risk_managment import StaticPipManager, TrailingPipManager
from TradeTide.loader import get_data_path
from TradeTide.position_collection import PositionCollection
from TradeTide.currencies import Currency
from datetime import datetime, timedelta
from TradeTide.signal import Signal

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
    spread_override=1,
    is_bid_override=True
)

# market.plot()

signal = Signal(market=market)

signal.generate_random(probability=0.03)

signal.display_signal()

risk_managment = StaticPipManager(
    stop_loss=10,
    take_profit=10
)


position_collection = PositionCollection(
    market=market,
    signal=signal,
    risk_managment=risk_managment,
    save_price_data=True,
)

position_collection.run()

position_collection.display()
position_collection.plot(max_positions=2)
