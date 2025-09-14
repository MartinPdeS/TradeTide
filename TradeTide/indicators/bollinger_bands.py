import numpy as np
import datetime
import matplotlib.pyplot as plt
from MPSPlots import helper
from pydantic.dataclasses import dataclass

from TradeTide.binary.interface_indicators import BOLLINGERBANDS
from TradeTide.indicators.base import BaseIndicator
from TradeTide.simulation_settings import SimulationSettings
from TradeTide.utils import config_dict


@dataclass(config=config_dict)
class BollingerBands(BOLLINGERBANDS, BaseIndicator):
    """
    Implements a Bollinger Bands indicator as an extension of the BaseIndicator class.

    This indicator consists of a middle band (the simple moving average) and two outer bands (the standard deviations).
    It is commonly used to identify overbought or oversold conditions in a market.

    Attributes
    ----------
    window : datetime.timedelta
        The window size for the moving average.
    multiplier float
        The number of standard deviations to use for the outer bands.

    Methods
    -------
    run: Runs the RMI indicator on the provided market data.
    plot: Plots the short and long moving averages on a given Matplotlib axis.
    """

    window: datetime.timedelta
    multiplier: float

    def __post_init__(self):
        window = (
            self.window.total_seconds()
            / SimulationSettings().get_time_unit().total_seconds()
        )

        super().__init__(window=int(window), multiplier=self.multiplier)

    @helper.pre_plot(nrows=1, ncols=1)
    def plot(self, axes: plt.Axes, show_metric: bool = False) -> None:
        """
        Plot price, Bollinger Bands, and trading signals on the given axis.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axis on which to draw the Bollinger Bands chart.
        """
        sma = np.asarray(self._cpp_sma)
        upper = np.asarray(self._cpp_upper_band)
        lower = np.asarray(self._cpp_lower_band)

        if show_metric:
            # price and bands
            axes.plot(
                self.market.dates,
                sma,
                label=f"SMA ({self.window})",
                linestyle="-",
                linewidth=1,
            )
            axes.plot(
                self.market.dates,
                upper,
                label=rf"Upper Band (+{self.multiplier} $\sigma$)",
                linestyle="--",
                linewidth=1,
            )
            axes.plot(
                self.market.dates,
                lower,
                label=rf"Lower Band (-{self.multiplier} $\sigma$)",
                linestyle="--",
                linewidth=1,
            )

        # fill the band region
        axes.fill_between(
            self.market.dates,
            lower,
            upper,
            where=~np.isnan(sma),
            interpolate=True,
            alpha=0.7,
            label="Band Range",
        )

        self._add_region_to_ax(ax=axes)

        self.market.plot_ask(axes=axes, show=False)

        axes.legend(loc="upper left")
