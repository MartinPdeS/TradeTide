#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

import pandas
import numpy
from typing import NoReturn
import matplotlib
from TradeTide.strategy.base_strategy import BaseStrategy


class MovingAverageCrossing(BaseStrategy):
    """
    Implements a Moving Average Crossing strategy as an extension of the BaseStrategy class.

    This strategy involves two moving averages of a series: a "short" and a "long" moving average. A typical trading signal
    is generated when the short moving average crosses above (bullish signal) or below (bearish signal) the long moving average.
    The strategy is commonly used to identify the momentum and direction of a trend.

    Attributes:
        short_window (int): The window size of the short moving average.
        long_window (int): The window size of the long moving average.
        min_period (int): The minimum number of observations in the window required to have a value (otherwise result is NA).
        value_type (str): The type of price data to use for the moving average calculation. Typically one of ['high', 'low', 'open', 'close'].

    Methods:
        add_to_ax: Plots the short and long moving averages on a given Matplotlib axis.
    """

    def __init__(
            self,
            short_window: int = 30,
            long_window: int = 150,
            min_period: int = 10,
            value_type: str = 'close'):
        """
        Initializes a new instance of the MovingAverageCrossing strategy with specified parameters.

        Parameters:
            short_window (int): Number of periods to use for the short moving average. Default is 30.
            long_window (int): Number of periods to use for the long moving average. Default is 150.
            min_period (int): Minimum number of observations in the window required to perform the operation. Default is 10.
            value_type (str): The type of price to be used in the moving average calculation. Default is 'close'.
        """

        self.short_window = short_window
        self.long_window = long_window
        self.min_period = min_period
        self.value_type = value_type

    def add_to_ax(self, ax: matplotlib.axes.Axes) -> NoReturn:
        """
        Adds the short and long moving average plots to the specified Matplotlib axis.

        This method visualizes the short and long moving averages on a plot, which is useful for identifying potential
        crossover points that might indicate trading signals.

        Parameters:
            ax (matplotlib.axes.Axes): The Matplotlib axis object where the moving averages will be plotted.
        """
        ax.plot(
            self.data['short_window_array'],
            linewidth=2,
            label='long window'
        )

        ax.plot(
            self.data['long_window_array'],
            label='short window',
            linewidth=2,
        )
        ax.set_ylabel('SMA crossing')

    @BaseStrategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        """
        Generates trading signals based on the crossover of short-term and long-term moving averages.

        This method applies a rolling mean calculation to a specified column (`self.value_type`) in the input DataFrame,
        creating two new columns: 'long_window_array' and 'short_window_array', representing the long-term and short-term
        moving averages, respectively. A trading signal is generated when the short-term moving average crosses above the
        long-term moving average, indicated by a value of 1 in the 'signal' column; otherwise, the 'signal' value is set to 0.

        The method is decorated with `@BaseStrategy.post_generate_signal`, suggesting it may perform additional operations
        or checks defined in the `BaseStrategy` class after the signal generation.

        Parameters:
            dataframe (pandas.DataFrame): The input DataFrame containing market data. It must include a column named
                                          as specified by `self.value_type`, which is used for calculating moving averages.

        Returns:
            pandas.DataFrame: The original DataFrame is modified in-place to include three new columns:
                              'long_window_array', 'short_window_array', and 'signal'. The 'signal' column contains
                              the generated trading signals based on the moving average crossover strategy.
        """
        self.data['long_window_array'] = self.data[self.value_type].rolling(
            window=self.long_window,
            min_periods=self.min_period
        ).mean(engine='numba')

        self.data['short_window_array'] = self.data[self.value_type].rolling(
            window=self.short_window,
            min_periods=self.min_period
        ).mean(engine='numba')

        self.data['signal'] = numpy.where(self.data['short_window_array'] > self.data['long_window_array'], 1, 0)
# -
