from TradeTide.tools import get_dataframe
from TradeTide.backtester import BackTester
from TradeTide.strategy import MovingAverageCrossing, RelativeStrengthIndex, Random


dataframe = get_dataframe('eur', 'usd', year=2020)

sub_frame = dataframe[:30_000].copy()


strategy = RelativeStrengthIndex(
    period=100,
    oversold_threshold=40,
    overbought_threshold=60
)

strategy = Random()

strategy.generate_signal(sub_frame)


backtester = BackTester(
    dataframe=sub_frame,
    strategy=strategy,
)

portfolio, metadata = backtester.back_test(
    stop_loss=0.001,
    take_profit=0.001,
    initial_capital=100_000,
    buy_unit=1_000,
    return_extra_data=True
)

backtester.plot(
    # show_holdings=False,
    show_take_win=True,
    show_stop_loss=True,
    show_totals=True,
    # show_cash=True,
)


