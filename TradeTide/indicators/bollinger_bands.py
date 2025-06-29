
import numpy as np
from TradeTide.binary.interface_indicators import BOLLINGERBANDS
from TradeTide.market import Market
from datetime import timedelta
import matplotlib.pyplot as plt
from TradeTide.indicators.base import BaseIndicator


class BollingerBands(BOLLINGERBANDS, BaseIndicator):
    """
    Implements a Bollinger Bands indicator as an extension of the BaseIndicator class.

    This indicator consists of a middle band (the simple moving average) and two outer bands (the standard deviations).
    It is commonly used to identify overbought or oversold conditions in a market.

    Attributes:
        window (int | str): The window size for the moving average.
        multiplier (int | float): The number of standard deviations to use for the outer bands.

    Methods:
        plot: Plots the Bollinger Bands on a given Matplotlib axis.
    """
    def __init__(self, window: timedelta, multiplier: float):
        self.window = window
        self.multiplier = multiplier

        super().__init__()

    def run(self, market: Market) -> None:
        """
        Runs the Bollinger Bands indicator on the provided market data.
        This method initializes the indicator with the market's dates and calculates the moving average
        and standard deviation based on the specified window size.

        Parameters
        ----------
        market (Market):
            The market data to run the indicator on. It should contain the dates and price data.

        Raises
        -------
        ValueError: If the market does not contain enough data points to calculate the moving averages.
        """
        self.market = market
        time_delta = market.dates[1] - market.dates[0]

        self._cpp_window = int(self.window / time_delta)
        self._cpp_multiplier = self.multiplier

        self._cpp_run_with_market(market)


    @BaseIndicator._pre_plot
    def plot(self, ax: plt.Axes, show_metric: bool = False) -> None:
        """
        Plot price, Bollinger Bands, and trading signals on the given axis.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axis on which to draw the Bollinger Bands chart.
        """
        sma     = np.asarray(self._cpp_sma)
        upper   = np.asarray(self._cpp_upper_band)
        lower   = np.asarray(self._cpp_lower_band)

        if show_metric:
            # price and bands
            ax.plot(
                self.market.dates,
                sma,
                label=f'SMA ({self.window})',
                linestyle='-',
                linewidth=1
            )
            ax.plot(
                self.market.dates,
                upper,
                label=rf'Upper Band (+{self.multiplier} $\sigma$)',
                linestyle='--',
                linewidth=1
            )
            ax.plot(
                self.market.dates,
                lower,
                label=rf'Lower Band (-{self.multiplier} $\sigma$)',
                linestyle='--',
                linewidth=1
            )

        # fill the band region
        ax.fill_between(
            self.market.dates,
            lower,
            upper,
            where=~np.isnan(sma),
            interpolate=True,
            alpha=0.2,
            label='Band Range'
        )

        ax.legend(loc='upper left')