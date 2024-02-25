#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

import matplotlib.pyplot as plt
import pandas
import numpy
from TradeTide.strategy import Strategy
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
        strategy (Strategy): An instance of a strategy class that implements an `add_to_ax` method,
                                 which adds strategy-specific metrics or indicators to a matplotlib axis.
    """

    def __init__(
            self,
            back_tester: object,
            market: pandas.DataFrame,
            portfolio: pandas.DataFrame,
            strategy: Strategy):
        """
        Initializes the PlotTrade object with market data, portfolio information, and a trading strategy.

        Parameters:
            market (pandas.DataFrame): The market data to be plotted, including dates and prices.
            portfolio (pandas.DataFrame): The portfolio data including dates, asset totals, and trading positions.
            strategy (Strategy): The trading strategy object which contains logic to add strategy-specific
                                     indicators to the plot.
        """
        self.backtester = back_tester
        self.market = market
        self.portfolio = portfolio
        self.strategy = strategy

    def construct_figure(
            self,
            show_price: bool = True,
            show_metric: bool = False,
            show_assets: bool = False,
            show_units: bool = False,
            show_positions: bool = False) -> NoReturn:
        """
        Constructs and displays a comprehensive figure that visualizes various aspects of the trading strategy,
        including market prices, trading signals, portfolio metrics, and specific indicators related to assets
        and positions. This visualization aids in analyzing the strategy's performance and decision-making process over time.

        Parameters:
            show_price (bool, optional): If True, includes a plot of market prices and trading signals. Default is True.
            show_metric (bool, optional): If True, includes a plot of strategy-specific performance metrics. Default is False.
            show_assets (bool, optional): If True, includes a plot of assets over time, reflecting the portfolio's composition. Default is False.
            show_positions (bool, optional): If True, includes a plot of the trading positions over time, showing when and how the strategy enters or exits trades. Default is False.
            show_units (bool, optional): If True, includes a plot of the trading units over time, showing when and how the strategy enters or exits trades. Default is False.

        Returns:
            None: This method does not return a value. Instead, it displays the constructed matplotlib figure directly.

        Notes:
            - The method organizes the selected plots into subplots within a single figure, with each subplot dedicated to one of the specified components (price, metric, assets, positions).
            - The subplots share the x-axis, which typically represents time, to facilitate comparative analysis across different aspects of the trading strategy.
            - Additional customization options for each subplot, such as legends, axes labels, and plot styles, can be specified within the respective plotting methods called within this method.
        """
        n_axis = numpy.sum([show_price, show_metric, show_assets, show_positions, show_units])

        title: str = 'Trading Strategy Overview'

        figure, axis = plt.subplots(
            nrows=n_axis,
            ncols=1,
            figsize=(12, 2 * n_axis),
            sharex=True,
            squeeze=False
        )

        figure.suptitle(title)

        plot_methods = [
            (show_price, self.add_price_and_signal_to_ax),
            (show_metric, self.add_strategy_to_ax),
            (show_positions, self.add_position_to_ax),
            (show_assets, self.add_asset_to_ax),
            (show_units, self.add_units_to_ax)
        ]

        axis_number = 0
        for show, method in plot_methods:
            if show:
                ax = axis[axis_number, 0]
                method(ax=ax)
                ax.set_axisbelow(True)
                self.add_buy_sell_signal_to_ax(ax=ax)
                self._format_legend(ax=ax)
                axis_number += 1

        plt.subplots_adjust(wspace=0, hspace=0.15)

        plt.xticks(rotation=45)
        plt.show()

        return figure

    def add_position_to_ax(self, ax: plt.Axes) -> None:
        """
        Visualizes the cumulative positions held over time on a specified Matplotlib axis. This visualization
        helps in understanding how the trading strategy's positions change throughout the trading period.

        The cumulative positions are calculated by summing up individual holdings from all positions in the
        portfolio at each point in time. This aggregated view provides insight into the overall exposure of
        the trading strategy at any given moment.

        Parameters:
            ax (plt.Axes): The Matplotlib Axes object where the positions data will be plotted.

        Note:
            This method assumes that each position in the portfolio has a 'holding' attribute, which is a
            DataFrame or Series indicating the holding status (1 for holding, 0 for not holding) over time.
        """
        ax.set_ylabel('Positions')

        # Plot the cumulative positions over time
        ax.plot(
            self.portfolio.index,
            self.portfolio.positions,
            linewidth=2,
            color='C0',
            label='Cumulative Positions'
        )

    def add_units_to_ax(self, ax: plt.Axes) -> None:
        """
        Visualizes the total units held in the trading portfolio over time on a specified Matplotlib axis. This plot
        aggregates the units from all positions in the portfolio, providing insight into the portfolio's exposure in
        terms of quantity over the trading period.

        Parameters:
            ax (plt.Axes): The Matplotlib Axes object where the units data will be plotted.

        Note:
            This method assumes that each position in the 'position_list' has a 'holding' attribute indicating
            whether the position is held (1 for holding, 0 for not holding) and a 'units' attribute representing
            the number of units held in each position. The 'holding' attribute should align with the 'market' index.
        """
        ax.set_ylabel('Units')

        # Plot the total units over time
        ax.plot(
            self.portfolio.index,
            self.portfolio.units,
            linewidth=2,
            color='C0',
            label='Total Units'
        )

    def add_asset_to_ax(self, ax: plt.Axes) -> None:
        """
        Visualizes the composition of the trading portfolio over time on a specified Matplotlib axis. This includes
        plots for the total portfolio value, cash component, and holdings value, providing a comprehensive view of
        the portfolio's financial status throughout the trading period.

        Parameters:
            ax (plt.Axes): The Matplotlib Axes object where the portfolio components will be plotted.

        Note:
            This method assumes the portfolio DataFrame contains 'total', 'cash', and 'holdings' columns,
            representing the total portfolio value, cash amount, and value of holdings over time, respectively.
        """
        ax.set_ylabel('Portfolio Value')

        # ax.plot(
        #     self.portfolio.index,
        #     self.portfolio.holdings_value,
        #     label='Holdings Value',
        #     linewidth=2,
        #     color='C0'
        # )

        ax.plot(
            self.portfolio.index,
            self.portfolio.cash,
            label='Cash',
            linewidth=2,
            color='C1'
        )

        ax.plot(
            self.portfolio.index,
            self.portfolio.total,
            label='Total',
            linewidth=2,
            color='black'
        )

    def add_strategy_to_ax(self, ax: plt.Axes) -> NoReturn:
        """
        Adds strategy-specific metrics or indicators to a specified matplotlib axis. This method utilizes the
        `add_to_ax` method of the strategy object, allowing for flexible integration of various strategy indicators.

        Parameters:
            ax (plt.Axes): The matplotlib axis object to which the strategy metrics will be added.
        """
        self.strategy.add_to_ax(ax)

    def add_price_and_signal_to_ax(self, ax: plt.Axes) -> NoReturn:
        """
        Plots the market closing prices and trading signals (buy/sell) on a specified matplotlib axis. This method
        provides a visual representation of when trades were opened or closed in relation to the market price movements.

        Parameters:
            ax (plt.Axes): The matplotlib axis object to which the price and signal information will be added.
        """
        ax.set_ylabel('Price')

        # Price and signals plot
        ax.plot(
            self.market['close'],
            label='Close Price',
            color='C0',
            linewidth=2
        )

        # Aggregate units from all positions in the portfolio
        for position in self.backtester.position_list:
            position.add_stop_loss_to_ax(ax=ax)

    def add_buy_sell_signal_to_ax(self, ax: plt.Axes) -> NoReturn:
        ax.fill_between(
            x=self.market.index,
            y1=0,
            y2=1,
            where=self.strategy.data['signal'] == -1,
            color='red',
            label='Sell signal',
            alpha=0.2,
            transform=ax.get_xaxis_transform(),
        )

        ax.fill_between(
            x=self.market.index,
            y1=0,
            y2=1,
            where=self.strategy.data['signal'] == +1,
            color='green',
            label='Buy signal',
            alpha=0.2,
            transform=ax.get_xaxis_transform(),
        )

    def add_stop_loss_take_profit_to_ax(self, ax: plt.Axes) -> NoReturn:
        discontinuity = self.portfolio.stop_loss_price.diff() != 0

        stop_loss = self.portfolio.stop_loss_price.copy()
        take_profit = self.portfolio.take_profit_price.copy()

        stop_loss[discontinuity] = numpy.nan
        take_profit[discontinuity] = numpy.nan

        ax.plot(
            stop_loss,
            color='red',
            label='stop-loss',
            linewidth=2
        )

        ax.plot(
            take_profit,
            color='green',
            label='take-profit',
            linewidth=2
        )

    def add_position_holding_to_ax(self, ax: plt.Axes) -> NoReturn:
        """
        Visualizes trading positions as shaded regions on the price plot, indicating periods where trades are
        held. It also plots stop-loss and take-profit levels, providing a clear view of trade management strategies.

        Parameters:
            ax (plt.Axes): The matplotlib axis object to which the position holding information will be added.
        """
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
                    y=[0, 1],
                    x1=start_date,
                    x2=end_date,
                    color='gray',
                    alpha=0.3,
                    transform=ax.get_xaxis_transform(),
                )

    def _format_legend(self, ax: plt.Axes) -> NoReturn:
        """
        Removes duplicate entries from the legend of a given matplotlib axis. This method ensures that each
        legend entry is unique, improving the clarity of the plot.

        Parameters:
            ax (plt.Axes): The matplotlib axis object from which to remove duplicate legend entries.
        """
        handles, labels = ax.get_legend_handles_labels()
        if len(labels) <= 1:
            return
        unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
        ax.legend(*zip(*unique), loc='upper right', facecolor='white', framealpha=1)


# -
