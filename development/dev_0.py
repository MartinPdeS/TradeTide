from TradeTide.market import Market
from TradeTide.binary.interface_exit_strategy import StaticExitStrategy, TrailingExitStrategy, BreakEvenExitStrategy
from TradeTide.portfolio import Portfolio
from TradeTide.loader import get_data_path
from TradeTide.position_collection import PositionCollection
from TradeTide.currencies import Currency
from datetime import datetime, timedelta
from TradeTide.signal import Signal
from TradeTide.binary.interface_capital_management import FixedFractionalCapitalManagement

market = Market()


now = datetime.now()
tomorrow = now + timedelta(days=1)
interval = timedelta(minutes=1)


filename = get_data_path('cad', 'usd', year=2023)

market.load_from_database(
    currency_0=Currency.CAD,
    currency_1=Currency.USD,
    year=2023,
    time_span=timedelta(hours=30),
    spread_override=1,
    is_bid_override=True
)
market.pip_value = 0.0001


signal = Signal(market=market)

signal.generate_random(probability=0.03 * 4)

# signal.display_signal()

exit_strategy = StaticExitStrategy(
    stop_loss=5,
    take_profit=5,
    save_price_data=True
)


position_collection = PositionCollection(
    market=market,
    signal=signal,
    exit_strategy=exit_strategy,
)

position_collection.run()

position_collection.display()

capital_management = FixedFractionalCapitalManagement(
    capital=1000,
    risk_per_trade=1,
    max_lot_size=10,
    max_capital_at_risk=100000,
    max_concurrent_positions=5,
)

portfolio  = Portfolio(
    capital_management=capital_management,
    position_collection=position_collection,
)

portfolio.simulate()


portfolio.display()

portfolio.plot()
