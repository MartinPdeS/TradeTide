from TradeTide.tools import get_dataframe
from TradeTide.metrics import RollingAverage
from TradeTide.strategy import Strategy
import matplotlib.pyplot as plt


dataframe = get_dataframe('eur', 'usd', year=2019)

sub_frame = dataframe[:305000].copy()

strategy = Strategy(
    dataframe=sub_frame,
    metric_0=RollingAverage(200, 8),
    metric_1=RollingAverage(50, 8),
    column='high'
)

portfolio = strategy.test()

portfolio.plot(x='date', y='total')
plt.show()

