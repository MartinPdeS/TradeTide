import numpy as np
import datetime
import matplotlib.pyplot as plt
from MPSPlots import helper

from pydantic.dataclasses import dataclass
from TradeTide.binary.interface_indicators import RELATIVEMOMENTUMINDEX
from TradeTide.indicators.base import BaseIndicator
from TradeTide.simulation_settings import SimulationSettings
from TradeTide.utils import config_dict


@dataclass(config=config_dict)
class RelativeMomentumIndex(RELATIVEMOMENTUMINDEX, BaseIndicator):
    """
    Implements a Relative Momentum Index (RMI) indicator as an extension of the BaseIndicator class.

    This indicator measures the momentum of price changes relative to a specified lookback period.
    It is commonly used to identify over_bought or over_sold conditions in a market.

    Attributes
    ----------
    momentum_period : datetime.timedelta
        The lookback period for the momentum calculation.
    smooth_window : datetime.timedelta
        The window size for smoothing the momentum values.
    over_bought : float
        The over_bought threshold.
    over_sold : float
        The over_sold threshold.

    Methods
    -------
    run: Runs the RMI indicator on the provided market data.
    plot: Plots the short and long moving averages on a given Matplotlib axis.
    """

    momentum_period: datetime.timedelta
    smooth_window: datetime.timedelta
    over_bought: float = 70.0
    over_sold: float = 30.0

    def __post_init__(self):
        _momentum_period = (
            self.momentum_period.total_seconds()
            / SimulationSettings().get_time_unit().total_seconds()
        )

        _smooth_window = (
            self.smooth_window.total_seconds()
            / SimulationSettings().get_time_unit().total_seconds()
        )

        super().__init__(
            momentum_period=int(_momentum_period),
            smooth_period=int(_smooth_window),
            over_bought=self.over_bought,
            over_sold=self.over_sold,
        )

    @helper.pre_plot(nrows=1, ncols=1)
    def plot(self, axes: plt.Axes) -> None:
        """
        Plot RMI, thresholds, and crossover signals on the given axis.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axis on which to draw the RMI chart.
        """
        dates = np.asarray(self.market.dates)
        price = np.asarray(self.market.ask.close)
        rmi = np.asarray(self._cpp_rmi)

        # plot price on secondary axis for context
        ax2 = axes.twinx()
        ax2.plot(dates, price, label="Price", color="gray", linewidth=0.5)
        ax2.set_ylabel("Price", color="gray")

        # plot RMI
        axes.plot(dates, rmi, label="RMI", color="blue", linewidth=1)
        # thresholds
        axes.hlines(
            [self._cpp_over_bought, self._cpp_over_sold],
            dates[0],
            dates[-1],
            colors=["red", "green"],
            linestyles="--",
            linewidth=1,
            label="Thresholds",
        )

        # labels and legend
        axes.set_xlabel("Date")
        axes.set_ylabel("RMI")

        self._unify_axes_legend(axes, ax2)

        self._add_region_to_ax(ax=axes)

        self.market.plot_ask(axes=axes, show=False)
