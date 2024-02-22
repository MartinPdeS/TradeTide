#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

import pandas
from typing import NoReturn
import matplotlib
from TradeTide.strategy.base_strategy import BaseStrategy


class RelativeStrengthIndex(BaseStrategy):
    """
    Implements the Relative Strength Index (RSI) trading strategy as an extension of the BaseStrategy class.

    The RSI is a momentum oscillator that measures the speed and change of price movements. It oscillates between 0 and 100.
    Traditionally, the RSI is considered overbought when above 70 and oversold when below 30. Signals can be generated from
    these conditions to suggest potential buy or sell opportunities.

    Attributes:
        period (int): The number of periods used to calculate the RSI. Commonly set to 14.
        overbought_threshold (int): The RSI level above which the asset is considered overbought. Typically set to 70.
        oversold_threshold (int): The RSI level below which the asset is considered oversold. Typically set to 30.
        value_type (str): The column name from the input DataFrame on which the RSI calculation is based. Usually set to 'close'.

    Methods:
        add_to_ax: Plots the RSI and its thresholds on a given Matplotlib axis.
        generate_signal: Calculates the RSI values based on price changes and generates buy/sell signals.
    """

    def __init__(
            self,
            period: int = 14,
            overbought_threshold: int = 70,
            oversold_threshold: int = 30,
            value_type: str = 'close'):
        """
        Initializes a new instance of the RelativeStrengthIndex strategy with specified parameters.

        Parameters:
            period (int): The lookback period for RSI calculation. Default is 14.
            overbought_threshold (int): The RSI value above which the market is considered overbought. Default is 70.
            oversold_threshold (int): The RSI value below which the market is considered oversold. Default is 30.
            value_type (str): The type of price to be used in RSI calculation (e.g., 'close', 'open'). Default is 'close'.
        """
        self.period = period
        self.overbought_threshold = overbought_threshold
        self.oversold_threshold = oversold_threshold
        self.value_type = value_type

    def add_to_ax(self, ax: matplotlib.axes.Axes) -> NoReturn:
        """
        Adds the RSI plot to the specified Matplotlib axis, including the overbought and oversold threshold lines.

        Parameters:
            ax (matplotlib.axes.Axes): The Matplotlib axis object where the RSI plot will be added.
        """
        ax.plot(
            self.data['rsi'],
            label='RSI',
            linewidth=2,
            color='grey'
        )

        ax.axhline(
            self.overbought_threshold,
            linestyle='--',
            color='red',
            alpha=0.5,
            linewidth=2,
            label='overbought'
        )

        ax.axhline(
            self.oversold_threshold,
            linestyle='--',
            color='green',
            alpha=0.5,
            linewidth=2,
            label='oversold'
        )

        ax.set_ylabel('RSI')

    @BaseStrategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        """
        Calculates the RSI based on the provided DataFrame and generates buy or sell signals.

        A buy signal is generated when the RSI crosses below the oversold threshold, and a sell signal is generated
        when the RSI crosses above the overbought threshold. The signals are added to the 'signal' column in the DataFrame.

        Parameters:
            dataframe (pandas.DataFrame): The input DataFrame containing price data and a column specified by `value_type`.

        Returns:
            pandas.DataFrame: The input DataFrame with an added 'rsi' column containing the RSI values and a 'signal' column
                              containing the buy/sell signals.
        """
        delta = self.data[self.value_type].diff()

        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()

        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()

        rs = gain / loss

        self.data['rsi'] = 100 - (100 / (1 + rs))

        self.data['signal'] = 0

        self.data.loc[self.data['rsi'] < self.oversold_threshold, 'signal'] = 1
        self.data.loc[self.data['rsi'] > self.overbought_threshold, 'signal'] = -1
