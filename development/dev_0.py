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
    stop_loss=5,
    take_profit=5,
    save_price_data=True
)


position_collection = PositionCollection(
    market=market,
    trade_signal=signal.trade_signal,
    exit_strategy=exit_strategy,
)

position_collection.open_positions()
position_collection.propagate_positions()

capital_management = capital_management.FixedFractional(
    capital=10000,
    risk_per_trade=0.1,
    max_capital_at_risk=100000,
    max_concurrent_positions=3,
)

portfolio  = Portfolio(
    capital_management=capital_management,
    position_collection=position_collection,
    save_history=True
)

portfolio.simulate()

# portfolio.display()
portfolio.plot(show=True)


# portfolio.plot_positions(max_positions=300, show=True)
