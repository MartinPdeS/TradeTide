#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from typing import NoReturn
import pandas as pd
import matplotlib
from TradeTide.indicators.base_indicator import BaseIndicator


class StochRSIIndicator(BaseIndicator):
    """
    Implements the Stochastic Relative Strength Index (StochRSI) trading indicator as an extension of the BaseIndicator class.

    StochRSI applies the Stochastic oscillator formula to a set of RSI values rather than standard price data. It's used to generate
    overbought and oversold signals within a bound range (0-1 or 0-100).

    Attributes:
        periods (int): The number of periods used to calculate the RSI and subsequently the StochRSI.
        rsi_periods (int): The number of periods used for calculating the underlying RSI.
        value_type (str): The column name from the input DataFrame on which the StochRSI calculation is based, usually 'close'.

    Methods:
        add_to_ax: Plots the StochRSI on a given Matplotlib axis.
        generate_signal: Calculates the StochRSI based on RSI movements and generates overbought/oversold signals.
    """

    def __init__(self, periods: int = 14, rsi_periods: int = 14, value_type: str = 'close'):
        """
        Initializes a new instance of the StochRSIIndicator with specified parameters.

        Parameters:
            periods (int): The lookback period for calculating the StochRSI. Default is 14.
            rsi_periods (int): The lookback period for calculating the underlying RSI. Default is 14.
            value_type (str): The type of price to be used in StochRSI calculation (e.g., 'close', 'open'). Default is 'close'.
        """
        self.periods = periods
        self.rsi_periods = rsi_periods
        self.value_type = value_type

    def add_to_ax(self, ax: matplotlib.axes.Axes) -> NoReturn:
        """
        Adds the StochRSI plot to the specified Matplotlib axis.

        This method plots the StochRSI values, providing a visual representation of overbought and oversold conditions.

        Parameters:
            ax (matplotlib.axes.Axes): The Matplotlib axis object where the StochRSI plot will be added.
        """
        ax.plot(
            self.data.index,
            self.data['stochrsi'],
            label='StochRSI',
            color='purple',
            linewidth=1
        )
        ax.axhline(y=0.8, color='red', linestyle='--', label='Overbought')
        ax.axhline(y=0.2, color='green', linestyle='--', label='Oversold')
        ax.set_ylabel('StochRSI')
        ax.legend()

    @BaseIndicator.post_generate_signal
    def generate_signal(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the StochRSI based on the provided DataFrame and generates overbought/oversold signals.

        Overbought signals (sell) are generated when StochRSI exceeds 0.8.
        Oversold signals (buy) are generated when StochRSI falls below 0.2.

        Parameters:
            market_data (pd.DataFrame): The input DataFrame containing price data.

        Returns:
            pd.DataFrame: The input DataFrame with added columns for RSI ('rsi'), StochRSI ('stochrsi'), and signals ('signal').
        """
        # Calculate RSI
        delta = market_data[self.value_type].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_periods).mean()
        rs = gain / loss
        self.data['rsi'] = 100 - (100 / (1 + rs))

        # Calculate StochRSI
        rsi_low = self.data['rsi'].rolling(window=self.periods).min()
        rsi_high = self.data['rsi'].rolling(window=self.periods).max()
        self.data['stochrsi'] = (self.data['rsi'] - rsi_low) / (rsi_high - rsi_low)

        # Generate signals
        self.data['signal'] = 0  # Default no action
        self.data.loc[self.data['stochrsi'] > 0.8, 'signal'] = -1  # Overbought (sell signal)
        self.data.loc[self.data['stochrsi'] < 0.2, 'signal'] = 1   # Oversold (buy signal)

        return self.data['signal']
# -
