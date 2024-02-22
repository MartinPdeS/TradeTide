from TradeTide.loader import get_market_data
from TradeTide.backtester import BackTester
from TradeTide.strategy import MovingAverageCrossing

market_data = get_market_data('jpy', 'usd', year=2023)

market_data = market_data[100:40000]


strategy = MovingAverageCrossing(short_window='20min', long_window='150min')

strategy.generate_signal(market_data)

strategy.plot()


backtester = BackTester(
    market=market_data,
    strategy=strategy,
)

portfolio, metadata = backtester.back_test(
    stop_loss='.1%',
    take_profit='.1%',
    initial_capital=100_000,
    buy_unit=1_000,
    return_extra_data=True,
    spread=0
)

print(portfolio['positions'])

backtester.plot()

# -
