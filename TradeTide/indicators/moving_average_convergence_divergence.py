#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from typing import NoReturn
import pandas

import matplotlib.pyplot as plt
from TradeTide.indicators.base_indicator import BaseIndicator


class MovingAverageConvergenceDivergence(BaseIndicator):
    """
    Implements the Moving Average Convergence Divergence (MACD) trading strategy as an extension of the BaseIndicator class.

    The MACD is a trend-following momentum indicator that shows the relationship between two moving averages of prices.
    It consists of the MACD line (the difference between the 12-day EMA and the 26-day EMA), the signal line (the 9-day EMA of the MACD line),
    and the MACD histogram (the difference between the MACD line and the signal line).

    Attributes:
        short_period (int): The period for the short-term EMA. Commonly set to 12.
        long_period (int): The period for the long-term EMA. Commonly set to 26.
        signal_period (int): The period for the signal line EMA. Commonly set to 9.
        value_type (str): The column name from the input DataFrame on which the MACD calculation is based, usually 'close'.

    Methods:
        add_to_ax: Plots the MACD line, signal line, and histogram on a given Matplotlib axis.
        generate_signal: Calculates the MACD line, signal line, and histogram, and generates buy/sell signals.
    """

    def __init__(
            self,
            short_period: int = 12,
            long_period: int = 26,
            signal_period: int = 9,
            value_type: str = 'close'):
        """
        Initializes a new instance of the MovingAverageConvergenceDivergence strategy with specified parameters.

        Parameters:
            short_period (int): The period for the short-term EMA. Default is 12.
            long_period (int): The period for the long-term EMA. Default is 26.
            signal_period (int): The period for the signal line EMA. Default is 9.
            value_type (str): The type of price to be used in MACD calculation (e.g., 'close', 'open'). Default is 'close'.
        """
        self.short_period = short_period
        self.long_period = long_period
        self.signal_period = signal_period
        self.value_type = value_type

    def add_to_ax(self, ax: plt.Axes) -> NoReturn:
        """
        Adds the MACD line, signal line, and histogram to the specified Matplotlib axis.

        Parameters:
            ax (plt.Axes): The Matplotlib axis object where the MACD plot will be added.
        """
        ax.plot(
            self.data['macd'],
            label='MACD',
            color='blue',
            linewidth=2
        )

        ax.plot(
            self.data['signal_line'],
            label='Signal Line',
            color='red',
            linewidth=2
        )

        ax.bar(
            self.data.index,
            self.data['histogram'],
            label='Histogram',
            color='grey',
            alpha=0.3
        )

        ax.legend()
        ax.set_ylabel('MACD')

    def get_features(self, drop_na: bool = True) -> pandas.DataFrame:
        features = self.data[['macd', 'signal_line', 'histogram']].copy()

        if drop_na:
            features.dropna(inplace=True)

        return features

    @BaseIndicator.post_generate_signal
    def generate_signal(self, market_data: pandas.DataFrame) -> pandas.DataFrame:
        """
        Calculates the MACD line, signal line, and histogram based on the provided DataFrame, and generates buy or sell signals.

        A buy signal is generated when the MACD line crosses above the signal line, and a sell signal is generated when the MACD line crosses below the signal line.

        Parameters:
            market_data (pandas.DataFrame): The input DataFrame containing price data and a column specified by `value_type`.

        Returns:
            pandas.DataFrame: The input DataFrame with added 'macd', 'signal_line', and 'histogram' columns, and a 'signal' column containing the buy/sell signals.
        """
        ema_short = self.data[self.value_type].ewm(span=self.short_period, adjust=False).mean()
        ema_long = self.data[self.value_type].ewm(span=self.long_period, adjust=False).mean()

        self.data['macd'] = ema_short - ema_long
        self.data['signal_line'] = self.data['macd'].ewm(span=self.signal_period, adjust=False).mean()
        self.data['histogram'] = self.data['macd'] - self.data['signal_line']

        self.data['signal'] = 0
        self.data.loc[self.data['histogram'] > 0, 'signal'] = 1  # Buy signal
        self.data.loc[self.data['histogram'] < 0, 'signal'] = -1  # Sell signal

        return self.data
