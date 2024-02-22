#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

import pandas
import numpy
from typing import NoReturn
import matplotlib
from TradeTide.strategy.base_strategy import BaseStrategy


class BollingerBands(BaseStrategy):
    """
    Implements the Bollinger Bands trading strategy as an extension of the BaseStrategy class.

    Bollinger Bands consist of a middle band being an N-period simple moving average (SMA), an upper band at K times an N-period
    standard deviation above the middle band, and a lower band at K times an N-period standard deviation below the middle band.
    These bands are used to determine overbought and oversold conditions in a market.

    Attributes
        periods (int): The number of periods used to calculate the SMA and standard deviation.
        deviation (float): The number of standard deviations away from the SMA the upper and lower bands should be set.
        value_type (str): The column name from the input DataFrame on which the Bollinger Bands calculation is based, usually 'close'.

    Methods:
        add_to_ax: Plots the Bollinger Bands on a given Matplotlib axis.
        generate_signal: Calculates the Bollinger Bands based on price movements and generates buy/sell signals.
    """

    def __init__(
            self,
            periods: int = 20,
            deviation: float = 2,
            value_type: str = 'close'):
        """
        Initializes a new instance of the BollingerBands strategy with specified parameters.

        Parameters:
            periods (int): The lookback period for calculating the moving average and standard deviation. Default is 20.
            deviation (float): The number of standard deviations to set the upper and lower bands from the moving average. Default is 2.
            value_type (str): The type of price to be used in Bollinger Bands calculation (e.g., 'close', 'open'). Default is 'close'.
        """
        self.periods = periods
        self.deviation = deviation
        self.value_type = value_type

    def add_to_ax(self, ax: matplotlib.axes.Axes) -> NoReturn:
        """
        Adds the Bollinger Bands plot to the specified Matplotlib axis.

        This method plots the upper and lower bands of the Bollinger Bands strategy, providing a visual representation
        of the market's overbought and oversold conditions.

        Parameters:
            ax (matplotlib.axes.Axes): The Matplotlib axis object where the Bollinger Bands plot will be added.
        """
        ax.plot(
            self.data.date,
            self.data['upper_band'],
            label='upper band',
            linewidth=2,
        )

        ax.plot(
            self.data.date,
            self.data['lower_band'],
            label='lower band',
            linewidth=2,
        )
        ax.set_ylabel('Bolliner Bands strategy')

    @BaseStrategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        """
        Calculates the Bollinger Bands based on the provided DataFrame and generates buy or sell signals.

        Buy signals are generated when the price crosses below the lower band, indicating a potential oversold condition.
        Sell signals are generated when the price crosses above the upper band, indicating a potential overbought condition.
        These signals are added to a 'signal' column in the DataFrame.

        Parameters:
            dataframe (pandas.DataFrame): The input DataFrame containing price data and a column specified by `value_type`.

        Returns:
            pandas.DataFrame: The input DataFrame with added columns for the moving average ('NA'), standard deviation ('STD'),
                              upper band ('upper_band'), lower band ('lower_band'), and buy/sell signals ('signal').
        """
        self.data['NA'] = self.data[self.value_type].rolling(window=self.periods).mean()

        self.data['STD'] = self.data[self.value_type].rolling(window=self.periods).std()

        self.data['upper_band'] = self.data['NA'] + (self.data['STD'] * self.deviation)

        self.data['lower_band'] = self.data['NA'] - (self.data['STD'] * self.deviation)

        # Generate buy signal when the close price crosses below the lower band
        self.data['signal'] = numpy.where(self.data['close'] < self.data['lower_band'], 1, 0)

        # Generate sell signal when the close price corsses above the upper band
        self.data['signal'] = numpy.where(self.data['close'] > self.data['lower_band'], -1, self.data['signal'])
# -
