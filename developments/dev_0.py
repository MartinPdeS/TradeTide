from TradeTide.loader import get_market_data
from TradeTide.backtester import BackTester
from TradeTide.strategy import RelativeStrengthIndex

dataframe = get_market_data('jpy', 'usd', year=2023)

market = dataframe[100:40000]


strategy = RelativeStrengthIndex(
    period=100,
    oversold_threshold=30,
    overbought_threshold=70
)

strategy.generate_signal(market)


backtester = BackTester(
    market=market,
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
