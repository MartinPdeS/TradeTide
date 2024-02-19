from TradeTide.tools import get_dataframe
from TradeTide.metrics import SimpleMovingAverage
from TradeTide.strategy import Strategy
import matplotlib.pyplot as plt

dataframe = get_dataframe('eur', 'usd', year=2020)


sub_frame = dataframe[:3_000].copy()

strategy = Strategy(
    dataframe=sub_frame,
    metric_0=SimpleMovingAverage(200, 8),
    metric_1=SimpleMovingAverage(50, 8),
    column='high'
)

portfolio, metadata = strategy.back_test(
    stop_loss=0.001,
    take_profit=0.001,
    initial_capital=100_000,
    buy_unit=1_000,
    return_extra_data=True
)

ax = metadata.plot.scatter(
    x='date',
    y='signal',
    figsize=(12, 4),
    label='signal',
    color='C0'
)

# metadata.plot.scatter(
#     ax=ax,
#     x='date',
#     y='positions',
#     label='positions',
#     color='C1'
# )


metadata['stop loss triggered'] = metadata['stop loss triggered'].astype(float)

metadata.plot.scatter(
    ax=ax,
    x='date',
    y='stop loss triggered',
    label='stop-loss triger',
    color='red',
    marker='x',

)


metadata['take profit triggered'] = metadata['take profit triggered'].astype(float)

metadata.plot.scatter(
    ax=ax,
    x='date',
    y='take profit triggered',
    label='take profit triger',
    color='green',
    marker='^',
)

ax_right = ax.twinx()

ax.set_yticks([])
ax_right.set_yticks([])

portfolio.plot(
    x='date',
    y='holdings',
    color='black',
    ax=ax_right
)

plt.show()

