import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_trading_strategy(market, portfolio, strategy, title='Trading Strategy Overview'):
    """
    Plots the trading strategy performance including price, buy/sell signals,
    and other relevant indicators like moving averages or RSI.

    Parameters:
    - data: DataFrame containing the historical data and trading indicators/signals.
    - title: str, optional. The title of the plot.
    """
    fig, axs = plt.subplots(2, 1, figsize=(7, 5), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
    fig.suptitle(title)
    axs[0].grid(False)

    # Price and signals plot
    axs[0].plot(
        market.date,
        market['close'],
        label='Close Price',
        color='skyblue'
    )

    axs[0].scatter(
        portfolio.date[portfolio['opened_positions'] == 1],
        market['close'][portfolio['opened_positions'] == 1],
        label='Buy Signal',
        marker='^',
        s=50,
        color='green',
        alpha=1,
        zorder=-1
    )

    axs[0].scatter(
        portfolio.date[portfolio['opened_positions'] == -1],
        market['close'][portfolio['opened_positions'] == -1],
        label='Sell Signal',
        marker='v',
        color='red',
        s=50,
        alpha=1,
        zorder=-1
    )

    strategy.add_to_ax(axs[1])

    # Customize the main plot
    axs[0].set_ylabel('Price')
    axs[0].legend()
    axs[0].grid(False)

    # Customize the indicators plot
    axs[1].legend()
    axs[1].grid(True)

    # Format the x-axis
    for ax in axs:
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    plt.xticks(rotation=45)
    plt.show()
