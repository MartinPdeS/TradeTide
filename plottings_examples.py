from TradeTide.tools import get_dataframe
from TradeTide.backtester import BackTester
import matplotlib.pyplot as plt
from TradeTide.strategy import MovingAverageCrossing, RelativeStrengthIndex


dataframe = get_dataframe('eur', 'usd', year=2020)

sub_frame = dataframe[:130_000].copy()

# strategy = MovingAverageCrossing(
#     long_window=150,
#     short_window=30,
#     min_period=10
# )

# strategy.generate_signal(sub_frame)


strategy = RelativeStrengthIndex(
    period=100,
    oversold_threshold=30,
    overbought_threshold=70
)

strategy.generate_signal(sub_frame)

# strategy.plot()


backtester = BackTester(
    dataframe=sub_frame,
    signal=strategy.signal,
)

portfolio, metadata = backtester.back_test(
    stop_loss=0.01,
    take_profit=0.01,
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

ax.legend(loc=2)
ax_right.legend(loc=1)


plt.show()

