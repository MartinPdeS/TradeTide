from TradeTide.tools import get_dataframe
from TradeTide.backtester import BackTester
from TradeTide.strategy import RelativeStrengthIndex

dataframe = get_dataframe('eur', 'usd', year=2020)

market = dataframe[20_000:40_000]


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

# print(portfolio['positions'])

backtester.plot()

# -
