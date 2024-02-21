import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas


def plot_metrics_on_ax(ax, market, portfolio, strategy):
    strategy.add_to_ax(ax)

    # Customize the indicators plot
    ax.legend()
    ax.grid(True)


def legend_without_duplicate_labels(ax):
    handles, labels = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
    ax.legend(*zip(*unique))


def plot_price_and_signal(ax, market, portfolio, strategy):
    ax.grid(False)

    # Price and signals plot
    ax.plot(
        market.date,
        market['close'],
        label='Close Price',
        color='C0',
        linewidth=2
    )

    ax.scatter(
        x=portfolio.date[portfolio['opened_positions'] == 1],
        y=market['close'][portfolio['opened_positions'] == 1],
        label='Buy Signal',
        marker='^',
        s=50,
        color='green',
        alpha=1,
        zorder=-1
    )

    ax.scatter(
        x=portfolio.date[portfolio['opened_positions'] == -1],
        y=market['close'][portfolio['opened_positions'] == -1],
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

    for i, row in portfolio.iterrows():
        if row.positions == 1:  # Buy signal
            start_date = row.date
            holding = True

        elif row.positions == -1 and holding:
            end_date = row.date
            holding = False

            ax.plot(
                [start_date, end_date],
                [row['stop_loss_price'], row['stop_loss_price']],
                color='red',
                label='stop-loss',
                linewidth=2
            )

            ax.plot(
                [start_date, end_date],
                [row['take_profit_price'], row['take_profit_price']],
                color='green',
                label='take-profit',
                linewidth=2
            )

            ax.fill_betweenx(
                y=[min_y, max_y],
                x1=start_date,
                x2=end_date,
                color='gray',
                alpha=0.3,
            )

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

    ax.legend()


def plot_trading_strategy(
        market: pandas.DataFrame,
        portfolio: pandas.DataFrame,
        strategy: object,
        title: str = 'Trading Strategy Overview'):
    """
    Plots the trading strategy performance including price, buy/sell signals,
    and other relevant indicators like moving averages or RSI.

    :param      market:     DataFrame containing the historical market data.
    :type       market:     pandas.DataFrame
    :param      portfolio:  DataFrame containing the portofolio values.
    :type       portfolio:  pandas.DataFrame
    :param      strategy:   The strategy adopted containing the technical indicators.
    :type       strategy:   object
    :param      title:      The title of the plot.
    :type       title:      str
    """
    fig, axs = plt.subplots(
        nrows=3,
        ncols=1,
        figsize=(10, 7),
        gridspec_kw={'height_ratios': [3, 1, 2]},
        sharex=True
    )

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

    legend_without_duplicate_labels(axs[0])
    plt.xticks(rotation=45)
    plt.show()
