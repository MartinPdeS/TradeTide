from TradeTide.tools import get_dataframe
from TradeTide.metrics import RollingAverage
from TradeTide.strategy import Strategy


dataframe = get_dataframe('eur', 'usd', year=2019)

sub_frame = dataframe[:800].copy()

strategy = Strategy(
    dataframe=sub_frame,
    metric_0=RollingAverage(200, 8),
    metric_1=RollingAverage(50, 8),
    column='high'
)


# a = sub_frame[sub_frame['buy signal'] == True]

# print(a)

strategy.plot()
