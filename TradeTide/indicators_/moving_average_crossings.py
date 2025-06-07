
import numpy as np
from TradeTide.binary.interface_indicators import MOVINGAVERAGECROSSING
from TradeTide.market import Market
from datetime import timedelta
from MPSPlots.styles import mps as plot_style
import matplotlib.pyplot as plt
from TradeTide.indicators_.base import BaseIndicator


class MovingAverageCrossing(MOVINGAVERAGECROSSING, BaseIndicator):
    """
    Implements a Moving Average Crossing (MAC) indicator as an extension of the BaseIndicator class.

    This indicator involves two moving averages of a series: a "short" and a "long" moving average. A typical trading signal
    is generated when the short moving average crosses above (bullish signal) or below (bearish signal) the long moving average.
    The indicator is commonly used to identify the momentum and direction of a trend.

    Attributes:
        short_window (int | str): The window size of the short moving average.
        long_window (int | str): The window size of the long moving average.

    Methods:
        plot: Plots the short and long moving averages on a given Matplotlib axis.
    """
    def __init__(self, short_window: timedelta, long_window: timedelta):
        self.short_window = short_window
        self.long_window = long_window

        super().__init__()

    def run(self, market: Market) -> None:
        """
        Runs the Moving Average Crossing indicator on the provided market data.
        This method initializes the indicator with the market's dates and calculates the short and long moving averages
        based on the specified window sizes.

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

        self._cpp_short_window = int(self.short_window / time_delta)
        self._cpp_long_window = int(self.long_window / time_delta)

        self._cpp_run_with_market(market)


    @BaseIndicator._pre_plot
    def plot(self, ax: plt.Axes) -> None:
        """
        Plots the moving averages and signals on the provided axis.

        Parameters
        ----------

        """
        dates = np.asarray(self.market.dates)
        signals = np.asarray(self._cpp_signals)
        golden_dates = dates[signals ==  1]
        death_dates  = dates[signals == -1]

        # draw vertical lines in one go
        ax.vlines(
            golden_dates,
            0, 1,
            colors='green',
            linestyles='--',
            alpha=0.5,
            linewidth=1,
            label='Golden Cross',
            transform=ax.get_xaxis_transform()
        )
        ax.vlines(
            death_dates, 0, 1,
            colors='red',
            linestyles='--',
            linewidth=1,
            alpha=0.5,
            label='Death Cross',
            transform=ax.get_xaxis_transform()
        )
