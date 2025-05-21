from TradeTide.market import Market
from TradeTide.portfolio import Portfolio
from TradeTide.loader import get_data_path
from TradeTide.position_collection import PositionCollection
from TradeTide.currencies import Currency
from datetime import datetime, timedelta
from TradeTide.signal import Signal
from TradeTide import capital_management, exit_strategy

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

signal = Signal(market=market)

signal.generate_random(probability=0.12)


exit_strategy = exit_strategy.Trailing(
    stop_loss=10,
    take_profit=10,
    save_price_data=True
)


position_collection = PositionCollection(
    market=market,
    signal=signal,
    exit_strategy=exit_strategy,
)

position_collection.open_positions()
position_collection.propagate_positions()

capital_management = capital_management.FixedFractional(
    capital=100000,
    risk_per_trade=0.01,
    max_lot_size=2,
    max_capital_at_risk=100000,
    max_concurrent_positions=1,
)

portfolio  = Portfolio(
    capital_management=capital_management,
    position_collection=position_collection,
)

portfolio.simulate()

portfolio.display()

portfolio.plot_positions(max_positions=300, show=True)
