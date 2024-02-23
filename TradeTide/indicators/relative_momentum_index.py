#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from typing import NoReturn
import pandas
import matplotlib.pyplot as plt
from TradeTide.indicators.base_indicator import BaseIndicator


class RelativeMomentumIndex(BaseIndicator):
    """
    Implements the Relative Momentum Index (RMI) trading indicator, an extension of the BaseIndicator class.

    The RMI is a variation of the Relative Strength Index (RSI) that accounts for the momentum of price movements by comparing
    the current price to the price 'n' periods ago, rather than the immediate last period. It oscillates between 0 and 100,
    where higher values typically indicate overbought conditions and lower values indicate oversold conditions.

    Attributes:
        period (int): The number of periods used to calculate the RMI.
        momentum (int): The lag period to compare the current price against for momentum calculation.
        overbought_threshold (int): The RMI level above which the asset is considered overbought. Commonly set to 70.
        oversold_threshold (int): The RMI level below which the asset is considered oversold. Commonly set to 30.
        value_type (str): The column name from the input DataFrame on which the RMI calculation is based, usually 'close'.

    Methods:
        add_to_ax: Plots the RMI and its thresholds on a given Matplotlib axis.
        generate_signal: Calculates the RMI values based on price changes and generates buy/sell signals.
    """

    def __init__(
            self,
            period: int = 14,
            momentum: int = 5,
            overbought_threshold: int = 70,
            oversold_threshold: int = 30,
            value_type: str = 'close'):
        """
        Initializes a new instance of the RelativeMomentumIndex indicator with specified parameters.

        Parameters:
            period (int): The lookback period for RMI calculation. Default is 14.
            momentum (int): The lag period to compare the current price against for momentum calculation. Default is 5.
            overbought_threshold (int): The RMI value above which the market is considered overbought. Default is 70.
            oversold_threshold (int): The RMI value below which the market is considered oversold. Default is 30.
            value_type (str): The type of price to be used in RMI calculation (e.g., 'close', 'open'). Default is 'close'.
        """
        self.period = period
        self.momentum = momentum
        self.overbought_threshold = overbought_threshold
        self.oversold_threshold = oversold_threshold
        self.value_type = value_type

    @BaseIndicator.shade_signal
    def add_to_ax(self, ax: plt.Axes) -> NoReturn:
        """
        Adds the RMI plot to the specified Matplotlib axis, including the overbought and oversold threshold lines.

        Parameters:
            ax (plt.Axes): The Matplotlib axis object where the RMI plot will be added.
        """
        ax.plot(
            self.data['rmi'],
            label='RMI',
            linewidth=2,
            color='blue'
        )

        ax.axhline(
            self.overbought_threshold,
            linestyle='--',
            color='red',
            alpha=0.5,
            linewidth=2,
            label='Overbought'
        )

        ax.axhline(
            self.oversold_threshold,
            linestyle='--',
            color='green',
            alpha=0.5,
            linewidth=2,
            label='Oversold'
        )

        ax.set_ylabel('RMI')

    @BaseIndicator.post_generate_signal
    def generate_signal(self, market_data: pandas.DataFrame) -> pandas.DataFrame:
        """
        Calculates the RMI based on the provided DataFrame and generates buy or sell signals.

        A buy signal is generated when the RMI crosses below the oversold threshold, and a sell signal is generated
        when the RMI crosses above the overbought threshold. The signals are added to the 'signal' column in the DataFrame.

        Parameters:
            market_data (pandas.DataFrame): The input DataFrame containing price data and a column specified by `value_type`.

        Returns:
            pandas.DataFrame: The input DataFrame with an added 'rmi' column containing the RMI values and a 'signal' column
                          containing the buy/sell signals.
        """
        # Calculate price differences compared to 'momentum' periods ago
        delta = self.data[self.value_type].diff(self.momentum)

        # Calculate gains and losses
        gain = delta.where(delta > 0, 0).rolling(window=self.period).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=self.period).mean()

        # Calculate the Relative Strength (RS)
        rs = gain / loss

        # Calculate the Relative Momentum Index (RMI)
        self.data['rmi'] = 100 - (100 / (1 + rs))

        # Initialize the 'signal' column
        self.data['signal'] = 0

        # Generate buy and sell signals
        self.data.loc[self.data['rmi'] < self.oversold_threshold, 'signal'] = 1  # Buy signal
        self.data.loc[self.data['rmi'] > self.overbought_threshold, 'signal'] = -1  # Sell signal

        return self.data

# -
