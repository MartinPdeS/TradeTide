
import numpy as np
from TradeTide.binary.interface_indicators import MOVINGAVERAGECROSSING
from TradeTide.market import Market
from datetime import timedelta
import matplotlib.pyplot as plt
from TradeTide.indicators.base import BaseIndicator


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
        Plots the raw price, both SMAs, the SMA-difference and the crossover signals
        on the provided axis.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axis to draw onto.
        """
        dates = np.asarray(self.market.dates)

        # get the two moving‐averages
        short_ma = np.asarray(self._cpp_short_moving_average)
        long_ma  = np.asarray(self._cpp_long_moving_average)
        diff_ma  = short_ma - long_ma

        # plot price and MAs
        ax.plot(
            dates,
            short_ma,
            label=f"Short MA ({self.short_window})",
            linestyle="--",
            linewidth=2
        )
        ax.plot(
            dates,
            long_ma,
            label=f"Long MA ({self.long_window})",
            linestyle="-",
            linewidth=2
        )

        # optional: show the difference on a secondary axis
        ax2 = ax.twinx()
        ax2.plot(dates, diff_ma, label="MA Diff (Short-Long)", linestyle=":", linewidth=1)
        ax2.set_ylabel("MA Difference")

        # combine legends
        lines, labels   = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines + lines2, labels + labels2, loc="upper left")

        # labels
        ax.set_xlabel("Date")
        ax.set_ylabel("Price / SMA")

        ax2.grid(False)
        ax2.set_zorder(-1)

