import numpy as np
from TradeTide.market import Market


class BaseIndicator:
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

        self._cpp_run_with_market(market)

    def _unify_axes_legend(self, *axes) -> None:
        """
        Unifies the legends of multiple axes into a single legend on the first axis.
        Parameters
        ----------
        *axes: matplotlib.axes.Axes
            The axes whose legends are to be unified.

        Returns
        -------
        None
        """
        lines = []
        labels = []
        for ax in axes:
            line, label = ax.get_legend_handles_labels()
            lines += line
            labels += label

        unique = dict(zip(labels, lines))
        axes[0].legend(unique.values(), unique.keys(), loc="upper left")

    def _add_region_to_ax(self, ax) -> None:
        """
        Adds colored regions to the provided axis based on the indicator's regions.
        Green regions indicate a positive signal, while red regions indicate a negative signal.

        Parameters
        ----------
        ax: matplotlib.axes.Axes
            The axis to which the regions will be added.

        Returns
        -------
        None
        """
        regions = np.asarray(self._cpp_regions)

        dates = np.array(self.market.dates)
        extended_dates = np.repeat(dates, 2)[1:-1]  # duplicate each interior date

        extended_regions = np.repeat(regions, 2)[:-2]

        mask_green = extended_regions == 1
        mask_red = extended_regions == -1

        ax.fill_between(
            extended_dates,
            0,
            1,
            where=mask_green,
            step="post",
            color="green",
            alpha=0.2,
            transform=ax.get_xaxis_transform(),
        )
        ax.fill_between(
            extended_dates,
            0,
            1,
            where=mask_red,
            step="post",
            color="red",
            alpha=0.2,
            transform=ax.get_xaxis_transform(),
        )
