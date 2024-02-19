from TradeTide.tools import get_dataframe
from TradeTide.metrics import SimpleMovingAverage
from TradeTide.strategy import Strategy
import matplotlib.pyplot as plt


dataframe = get_dataframe('eur', 'usd', year=2020)


sub_frame = dataframe[:100_000].copy()

strategy = Strategy(
    dataframe=sub_frame,
    metric_0=SimpleMovingAverage(200, 8),
    metric_1=SimpleMovingAverage(50, 8),
    column='high'
)

portfolio = strategy.back_test(
    stop_loss=0.1,
    take_profit=0.1,
    initial_capital=100_000,
    buy_unit=1_000,
)

portfolio['total'].plot()

plt.show()

