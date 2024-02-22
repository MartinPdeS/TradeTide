#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

import matplotlib.pyplot as plt
import pandas
from TradeTide.strategy.base_strategy import BaseStrategy
import matplotlib
from typing import NoReturn
import MPSPlots.render2D
# plt.style.use('ggplot')


class PlotTrade():
    """
    This class is designed to visualize trading strategies by plotting the market data,
    portfolio metrics, and trading signals based on a specified trading strategy. It integrates
    market price data, portfolio performance, and strategy indicators into a coherent set of
    matplotlib plots to provide a comprehensive overview of trading activity and strategy effectiveness.

    Attributes:
        market (pandas.DataFrame): DataFrame containing market data with at least 'date' and 'close' columns.
        portfolio (pandas.DataFrame): DataFrame containing portfolio metrics and trading signals,
                                      must include 'date', 'total', 'positions', 'opened_positions',
                                      'stop_loss_price', and 'take_profit_price' columns.
        strategy (BaseStrategy): An instance of a strategy class that implements an `add_to_ax` method,
                                 which adds strategy-specific metrics or indicators to a matplotlib axis.
    """

    def __init__(
            self,
            market: pandas.DataFrame,
            portfolio: pandas.DataFrame,
            strategy: BaseStrategy):
        """
        Initializes the PlotTrade object with market data, portfolio information, and a trading strategy.

        Parameters:
            market (pandas.DataFrame): The market data to be plotted, including dates and prices.
            portfolio (pandas.DataFrame): The portfolio data including dates, asset totals, and trading positions.
            strategy (BaseStrategy): The trading strategy object which contains logic to add strategy-specific
                                     indicators to the plot.
        """
        self.market = market
        self.portfolio = portfolio
        self.strategy = strategy

    def construct_figure(self) -> NoReturn:
        """
        Constructs and displays the trading strategy overview figure. This method organizes subplots into a
        single figure, representing market prices, trading signals, portfolio metrics, and strategy-specific
        indicators. It creates an interactive visualization to analyze the trading strategy's performance over time.

        This method does not return anything but shows the constructed matplotlib figure.
        """
        title: str = 'Trading Strategy Overview'

        self.figure, self.axis = plt.subplots(
            nrows=3,
            ncols=1,
            figsize=(10, 7),
            gridspec_kw={'height_ratios': [3, 2, 2]},
            sharex=True,
        )

        self.figure.suptitle(title)

        self.add_price_and_signal_to_ax(ax=self.axis[0])

        self.add_position_holding_to_ax(ax=self.axis[0])

        self.remove_duplicate_legend_from_ax(self.axis[0])

        self.add_metric_to_ax(ax=self.axis[1])

        self.add_asset_to_ax(ax=self.axis[2])

        plt.subplots_adjust(wspace=0, hspace=0.15)

        plt.xticks(rotation=45)
        plt.show()

    def remove_duplicate_legend_from_ax(self, ax: matplotlib.axes.Axes) -> NoReturn:
        """
        Removes duplicate entries from the legend of a given matplotlib axis. This method ensures that each
        legend entry is unique, improving the clarity of the plot.

        Parameters:
            ax (matplotlib.axes.Axes): The matplotlib axis object from which to remove duplicate legend entries.
        """
        handles, labels = ax.get_legend_handles_labels()
        unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
        ax.legend(*zip(*unique), facecolor='white', framealpha=1)

    def add_asset_to_ax(self, ax: matplotlib.axes.Axes):
        """
        Adds asset total over time to a specified matplotlib axis. This plot represents the total value of the
        trading portfolio over the duration of the trading data.

        Parameters:
            ax (matplotlib.axes.Axes): The matplotlib axis object to which the asset total plot will be added.
        """

        line_0 = ax.plot(
            self.portfolio.total,
            label='Total',
            linewidth=2,
            color='C0'
        )

        line_1 = ax.plot(
            self.portfolio.cash,
            label='Cash',
            linewidth=2,
            color='C1'
        )

        line_2 = ax.plot(
            self.portfolio.holdings,
            label='Holdings',
            linewidth=2,
            color='C2'
        )
        ax_twin = ax.twinx()

        line_3 = ax_twin.plot(
            self.portfolio.units,
            label='units',
            linewidth=2,
            color='C3'
        )

        lines = line_0 + line_1 + line_2 + line_3
        labels = [
            line.get_label() for line in lines
        ]

        ax_twin.legend(lines, labels, loc='upper left', facecolor='white', framealpha=1).set_zorder(100)
        ax_twin.set_axisbelow(True)
        ax.set_ylabel('Assets')
        ax_twin.set_ylabel('Units')

    def add_metric_to_ax(self, ax: matplotlib.axes.Axes) -> NoReturn:
        """
        Adds strategy-specific metrics or indicators to a specified matplotlib axis. This method utilizes the
        `add_to_ax` method of the strategy object, allowing for flexible integration of various strategy indicators.

        Parameters:
            ax (matplotlib.axes.Axes): The matplotlib axis object to which the strategy metrics will be added.
        """
        self.strategy.add_to_ax(ax)

        # Customize the indicators plot
        ax.legend(loc='upper right', facecolor='white', framealpha=1)
        ax.grid(True)

    def add_position_holding_to_ax(self, ax: matplotlib.axes.Axes) -> NoReturn:
        """
        Visualizes trading positions as shaded regions on the price plot, indicating periods where trades are
        held. It also plots stop-loss and take-profit levels, providing a clear view of trade management strategies.

        Parameters:
            ax (matplotlib.axes.Axes): The matplotlib axis object to which the position holding information will be added.
        """
        ax.set_axisbelow(True)
        min_y = self.market['close'].min()
        max_y = self.market['close'].max()

        # Shading holding periods
        holding = False

        for date, row in self.portfolio.iterrows():
            if row.opened_positions == 1:  # Buy signal
                start_date = date
                holding = True

            elif row.opened_positions == -1 and holding:
                end_date = date
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

    def add_price_and_signal_to_ax(self, ax: matplotlib.axes.Axes) -> NoReturn:
        """
        Plots the market closing prices and trading signals (buy/sell) on a specified matplotlib axis. This method
        provides a visual representation of when trades were opened or closed in relation to the market price movements.

        Parameters:
            ax (matplotlib.axes.Axes): The matplotlib axis object to which the price and signal information will be added.
        """
        ax.set_axisbelow(True)
        ax.grid(True)

        # Price and signals plot
        ax.plot(
            self.market['close'],
            label='Close Price',
            color='C0',
            linewidth=2
        )

        index_open_position = self.portfolio['opened_positions'] == 1
        index_close_position = self.portfolio['opened_positions'] == -1

        ax.scatter(
            x=self.portfolio.index[index_open_position],
            y=self.market['close'][index_open_position],
            label='Buy Signal',
            marker='^',
            s=50,
            color='green',
        )

        ax.scatter(
            x=self.portfolio.index[index_close_position],
            y=self.market['close'][index_close_position],
            label='Sell Signal',
            marker='v',
            color='red',
            s=50,
        )

        # Customize the main plot
        ax.set_ylabel('Price')
        ax.legend(loc='upper right', facecolor='white', framealpha=1)
        ax.grid(True)




