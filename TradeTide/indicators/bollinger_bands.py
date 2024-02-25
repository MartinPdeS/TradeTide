#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

import pandas
import numpy
from typing import NoReturn
import matplotlib
from TradeTide.indicators.base_indicator import BaseIndicator


class BollingerBands(BaseIndicator):
    """
    Implements the Bollinger Bands trading indicator as an extension of the BaseIndicator class.

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
        Initializes a new instance of the BollingerBands indicator with specified parameters.

        Parameters:
            periods (int): The lookback period for calculating the moving average and standard deviation. Default is 20.
            deviation (float): The number of standard deviations to set the upper and lower bands from the moving average. Default is 2.
            value_type (str): The type of price to be used in Bollinger Bands calculation (e.g., 'close', 'open'). Default is 'close'.
        """
        self.periods = periods
        self.deviation = deviation
        self.value_type = 'close'

    def add_to_ax(self, ax: matplotlib.axes.Axes) -> NoReturn:
        """
        Adds the Bollinger Bands plot to the specified Matplotlib axis.

        This method plots the upper and lower bands of the Bollinger Bands indicator, providing a visual representation
        of the market's overbought and oversold conditions.

        Parameters:
            ax (matplotlib.axes.Axes): The Matplotlib axis object where the Bollinger Bands plot will be added.
        """
        ax.fill_between(
            x=self.data.index,
            y1=self.data.lower_band,
            y2=self.data.upper_band,
            label='upper band',
            linewidth=1,
            color='black',
            alpha=0.2
        )

        ax.plot(
            self.data.close,
            label='close value',
            linewidth=1,
            color='C0'
        )

        ax.set_ylabel('Bolliner Bands indicator')

    @BaseIndicator.post_generate_signal
    def generate_signal(self, market_data: pandas.DataFrame) -> pandas.DataFrame:
        """
        Calculates the Bollinger Bands based on the provided DataFrame and generates buy or sell signals.

        Buy signals are generated when the price crosses below the lower band, indicating a potential oversold condition.
        Sell signals are generated when the price crosses above the upper band, indicating a potential overbought condition.
        These signals are added to a 'signal' column in the DataFrame.

        Parameters:
            market_data (pandas.DataFrame): The input DataFrame containing price data and a column specified by `value_type`.

        Returns:
            pandas.DataFrame: The input DataFrame with added columns for the moving average ('MA'), standard deviation ('STD'),
                              upper band ('upper_band'), lower band ('lower_band'), and buy/sell signals ('signal').
        """
        self.data['MA'] = self.data['close'].rolling(window=self.periods).mean()

        self.data['STD'] = self.data['close'].rolling(window=self.periods).std()

        self.data['upper_band'] = self.data['MA'] + (self.data['STD'] * self.deviation)

        self.data['lower_band'] = self.data['MA'] - (self.data['STD'] * self.deviation)

        # Generate buy signal when the close price crosses below the lower band
        self.data['signal'] = numpy.where(self.data['close'] < self.data['lower_band'], 1, 0)

        # Generate sell signal when the close price crosses above the upper band
        self.data['signal'] = numpy.where(self.data['close'] > self.data['upper_band'], -1, self.data['signal'])
# -
