import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_metrics_on_ax(ax, market, portfolio, strategy):
    strategy.add_to_ax(ax)

    # Customize the indicators plot
    ax.legend()
    ax.grid(True)


def plot_price_and_signal(ax, market, portfolio, strategy):
    ax.grid(False)

    # Price and signals plot
    ax.plot(
        market.date,
        market['close'],
        label='Close Price',
        color='skyblue'
    )

    ax.scatter(
        portfolio.date[portfolio['opened_positions'] == 1],
        market['close'][portfolio['opened_positions'] == 1],
        label='Buy Signal',
        marker='^',
        s=50,
        color='green',
        alpha=1,
        zorder=-1
    )

    ax.scatter(
        portfolio.date[portfolio['opened_positions'] == -1],
        market['close'][portfolio['opened_positions'] == -1],
        label='Sell Signal',
        marker='v',
        color='red',
        s=50,
        alpha=1,
        zorder=-1
    )

    min_y = market['close'].min()
    max_y = market['close'].max()

    # Shading holding periods
    holding = False
    for i in range(1, len(portfolio)):
        if portfolio['positions'].iloc[i] == 1:  # Buy signal
            start_date = portfolio.date[i]
            holding = True
        elif portfolio['positions'].iloc[i] == -1 and holding:  # Sell signal
            end_date = portfolio.date[i]

            ax.fill_betweenx(
                y=[min_y, max_y],
                x1=start_date,
                x2=end_date,
                color='gray',
                alpha=0.3,
            )
            holding = False

    # Customize the main plot
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid(False)


def plot_assets(ax, market, portfolio, strategy):
    ax.plot(
        portfolio.date,
        portfolio.total,
        label='Total',
        alpha=1,
        linewidth=2,
        zorder=-1
    )

    # ax.plot(
    #     portfolio.date,
    #     portfolio.holdings,
    #     label='holdings',
    #     alpha=1,
    #     linewidth=2,
    #     zorder=-1
    # )

    ax.legend()


def plot_trading_strategy(market, portfolio, strategy, title='Trading Strategy Overview'):
    """
    Plots the trading strategy performance including price, buy/sell signals,
    and other relevant indicators like moving averages or RSI.

    Parameters:
    - data: DataFrame containing the historical data and trading indicators/signals.
    - title: str, optional. The title of the plot.
    """
    fig, axs = plt.subplots(3, 1, figsize=(7, 7), gridspec_kw={'height_ratios': [3, 1, 2]}, sharex=True)
    fig.suptitle(title)

    plot_price_and_signal(
        ax=axs[0],
        market=market,
        portfolio=portfolio,
        strategy=strategy
    )

    plot_assets(
        ax=axs[2],
        market=market,
        portfolio=portfolio,
        strategy=strategy
    )

    plot_metrics_on_ax(
        ax=axs[1],
        market=market,
        portfolio=portfolio,
        strategy=strategy
    )

    # Format the x-axis
    for ax in axs:
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    plt.xticks(rotation=45)
    plt.show()
