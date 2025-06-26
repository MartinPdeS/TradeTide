
import numpy as np
from TradeTide.binary.interface_indicators import RELATIVEMOMENTUMINDEX
from TradeTide.market import Market
from datetime import timedelta
import matplotlib.pyplot as plt
from TradeTide.indicators.base import BaseIndicator


class RelativeMomentumIndex(RELATIVEMOMENTUMINDEX, BaseIndicator):
    """
    Implements a Relative Momentum Index (RMI) indicator as an extension of the BaseIndicator class.

    This indicator measures the momentum of price changes relative to a specified lookback period.
    It is commonly used to identify over_bought or over_sold conditions in a market.

    Attributes:
        momentum_period (int | str): The lookback period for the momentum calculation.
        smooth_window (int | str): The window size for smoothing the momentum values.
        over_bought (float): The over_bought threshold.
        over_sold (float): The over_sold threshold.

    Methods:
        plot: Plots the short and long moving averages on a given Matplotlib axis.
    """
    def __init__(self, momentum_period: timedelta, smooth_window: timedelta, over_bought: float = 70.0, over_sold: float = 30.0):

        self.momentum_period = momentum_period
        self.smooth_window = smooth_window
        self.over_bought = over_bought
        self.over_sold = over_sold

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

        self._cpp_momentum_period = int(self.momentum_period / time_delta)
        self._cpp_smooth_window = int(self.smooth_window / time_delta)
        self._cpp_over_bought = self.over_bought
        self._cpp_over_sold = self.over_sold

        self._cpp_run_with_market(market)

    @BaseIndicator._pre_plot
    def plot(self, ax: plt.Axes) -> None:
        """
        Plot RMI, thresholds, and crossover signals on the given axis.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axis on which to draw the RMI chart.
        """
        dates = np.asarray(self.market.dates)
        price = np.asarray(self.market.ask.close)
        rmi   = np.asarray(self._cpp_rmi)
        regions   = np.asarray(self._cpp_regions)

        # plot price on secondary axis for context
        ax2 = ax.twinx()
        ax2.plot(
            dates,
            price,
            label='Price',
            color='gray',
            linewidth=0.5
        )
        ax2.set_ylabel('Price', color='gray')

        # plot RMI
        ax.plot(
            dates,
            rmi,
            label='RMI',
            color='blue',
            linewidth=1
        )
        # thresholds
        ax.hlines(
            [self._cpp_over_bought, self._cpp_over_sold],
            dates[0], dates[-1],
            colors=['red','green'],
            linestyles='--',
            linewidth=1,
            label='Thresholds'
        )


        # labels and legend
        ax.set_xlabel('Date')
        ax.set_ylabel('RMI')
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        unique = dict(zip(labels+labels2, lines+lines2))
        ax.legend(unique.values(), unique.keys(), loc='upper left')
        plt.tight_layout()


