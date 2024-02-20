from TradeTide.tools import get_dataframe
from TradeTide.backtester import BackTester
from TradeTide.strategy import RelativeStrengthIndex
from TradeTide.plottings import plot_trading_strategy

dataframe = get_dataframe('eur', 'usd', year=2020)

market = dataframe[:100_000]


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
    stop_loss=0.01,
    take_profit=0.01,
    initial_capital=100_000,
    buy_unit=1_000,
    return_extra_data=True
)

plot_trading_strategy(
    market=market,
    portfolio=portfolio,
    strategy=strategy,
)
