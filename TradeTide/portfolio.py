from typing import Tuple, Optional, Union
import numpy as np

from TradeTide.binary import position
from TradeTide.binary.interface_portfolio import PORTFOLIO
import matplotlib.pyplot as plt
from MPSPlots.styles import mps
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from functools import wraps
import TradeTide

Long = position.Long
Short = position.Short


class Portfolio(PORTFOLIO):
    def __init__(self, position_collection, debug_mode: bool = False):
        """
        Initialize the Portfolio with a position collection and optional debug mode.

        Parameters
        ----------
        position_collection : PositionCollection
            The collection of positions to manage.
        """
        super().__init__(
            position_collection=position_collection,
            debug_mode=TradeTide.debug_mode if TradeTide.debug_mode else debug_mode
        )
        self.position_collection = position_collection

    def plot_positions(
        self,
        figure_size: Tuple[int, int] = (12, 4),
        max_positions: Union[int, float] = np.inf,
        show: bool = True
    ) -> plt.Figure:
        """
        Plot market bid/ask prices and shade closed positions, using the mps style,
        consistent naming of 'position', and a clear legend with distinct colors.

        Parameters
        ----------
        figsize : tuple[int, int], default=(12,4)
            Size of the figure in inches.
        max_positions : int or float, default=np.inf
            Maximum number of positions to draw (in chronological order).
        show : bool, default=True
            Whether to display the plot after creation.
        save_as : str, optional
            If provided, save the figure to this path.

        Returns
        -------
        plt.Figure : Figure and Axes objects for further customization or saving.

        """
        long_list = []
        short_list = []

        position_list = self.get_positions(max_positions)

        for idx, p in enumerate(position_list):
            if p.is_long:
                long_list.append(p)
            else:
                short_list.append(p)

            if idx > 10:
                break

        with plt.style.context(mps):
            # 1) Create or get axes
            figure, (ax_long, ax_short) = plt.subplots(ncols=1, nrows=2, figsize=figure_size, sharex=True)

            self._plot_long_positions(ax=ax_long, position_list=long_list, show=False)

            self._plot_short_positions(ax=ax_short, position_list=short_list, show=False)

            if show:
                plt.show()

            return figure

    def _pre_plot(function):
        """
        Decorator to set the matplotlib style and handle common plotting parameters.
        This decorator applies the MPS style and manages the axes, figure size, and saving options.
        """
        @wraps(function)
        def wrapper(self, ax: plt.Axes = None, figure_size: tuple = (12, 4), show: bool = True, save_as: str = None, **kwargs):

            with plt.style.context(mps):
                if ax is None:
                    _, ax = plt.subplots(1, 1, figsize=figure_size)

                function(self, ax=ax, **kwargs)
                ax.set_xlabel("Date")

                plt.tight_layout()

                if save_as is not None:
                    ax.figure.savefig(save_as, bbox_inches='tight')

                if show:
                    plt.show()

                return ax

        return wrapper

    @_pre_plot
    def _plot_long_positions(self, position_list: list[position.Long], ax: plt.Axes) -> plt.Axes:
        """
        Plot the long positions in the portfolio.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.

        Returns
        -------
        ax : matplotlib.axes.Axes
            The axes with the long positions plot.
        """
        color_fill   = "lightblue"
        sl_color    = "#d62728"
        tp_color    = "#2ca02c"

        ax.set_ylabel(f"Bid Price")

        self.position_collection.market.plot_bid(ax=ax, show=False)

        for position in position_list:
            start, end = position.start_date, position.close_date
            ax.axvspan(start, end, facecolor=color_fill, edgecolor="black", alpha=0.2)
            ax.plot(position.dates(), position.stop_loss_prices(), linestyle="--", color=sl_color, linewidth=1)
            ax.plot(position.dates(), position.take_profit_prices(), linestyle="--", color=tp_color, linewidth=1)

        # Custom legend
        legend_handles = [
            Line2D([0], [0], color=sl_color, linestyle="--", label="Stop Loss"),
            Line2D([0], [0], color=tp_color, linestyle="--", label="Take Profit"),
            Patch(facecolor=color_fill, edgecolor="none", label="Long Position"),
        ]

        ax.legend(handles=legend_handles, loc="upper left", framealpha=0.9)

    @_pre_plot
    def _plot_short_positions(self, position_list: list[position.Long], ax: plt.Axes) -> plt.Axes:
        """
        Plot the short positions in the portfolio.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.

        Returns
        -------
        ax : matplotlib.axes.Axes
            The axes with the long positions plot.
        """
        color_fill  = (0.8, 0.2, 0.2, 0.3)
        sl_color    = "#d62728"
        tp_color    = "#2ca02c"

        ax.set_ylabel(f"Bid Price")

        self.position_collection.market.plot_bid(ax=ax, show=False)

        for position in position_list:
            start, end = position.start_date, position.close_date
            ax.axvspan(start, end, facecolor=color_fill, edgecolor="black", alpha=0.2)
            ax.plot(position.dates(), position.stop_loss_prices(), linestyle="--", color=sl_color, linewidth=1)
            ax.plot(position.dates(), position.take_profit_prices(), linestyle="--", color=tp_color, linewidth=1)

        # Custom legend
        legend_handles = [
            Line2D([0], [0], color=sl_color, linestyle="--", label="Stop Loss"),
            Line2D([0], [0], color=tp_color, linestyle="--", label="Take Profit"),
            Patch(facecolor=color_fill, edgecolor="none", label="Short Position")
        ]

        ax.legend(handles=legend_handles, loc="upper left", framealpha=0.9)


    @_pre_plot
    def plot_equity(self, ax: plt.Axes) -> plt.Axes:
        """
        Plot the portfolio's equity over time.

        Parameters
        ----------
        show : bool, default=True
            Show the plot after creation.
        figure_size : tuple, default=(12, 4)
            Size of the figure in inches.
        ax : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.
        save_as : str, optional
            If provided, save the figure to this path.

        Returns
        -------
        ax : matplotlib.axes.Axes
            The axes with the equity plot.

        """
        ax.plot(self.record.time, self.record.equity, color='black')
        ax.axhline(self.record.initial_capital, color='red', linestyle='--', linewidth=1, label='Initial Capital')
        ax.set_ylabel("Equity")
        ax.legend()

    @_pre_plot
    def plot_capital_at_risk(self, ax: plt.Axes) -> plt.Axes:
        """
        Plot the capital at risk over time.

        Parameters
        ----------
        show : bool, default=True
            Show the plot after creation.
        figure_size : tuple, default=(12, 4)
            Size of the figure in inches.
        ax : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.
        save_as : str, optional
            If provided, save the figure to this path.

        Returns
        -------
        ax : matplotlib.axes.Axes
            The axes with the capital at risk plot.
        """
        ax.step(self.record.time, self.record.capital_at_risk, color='black', where='mid')
        ax.set_ylabel("Capital at Risk")

    @_pre_plot
    def plot_capital(self, ax: plt.Axes) -> plt.Axes:
        """
        Plot the capital over time.

        Parameters
        ----------
        show : bool, default=True
            Show the plot after creation.
        figure_size : tuple, default=(12, 4)
            Size of the figure in inches.
        ax : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.
        save_as : str, optional
            If provided, save the figure to this path.

        Returns
        -------
        ax : matplotlib.axes.Axes
            The axes with the capital plot.
        """
        ax.step(self.record.time, self.record.capital, color='black', where='mid')
        ax.set_ylabel("Capital")

    @_pre_plot
    def plot_number_of_positions(self, ax: Optional[plt.Axes] = None) -> plt.Axes:
        """
        Plot the number of open positions over time.

        Parameters
        ----------
        show : bool, default=True
            Show the plot after creation.
        figure_size : tuple, default=(12, 4)
            Size of the figure in inches.
        ax : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.
        save_as : str, optional
            If provided, save the figure to this path.

        Returns
        -------
        ax : matplotlib.axes.Axes
            The axes with the number of open positions plot.
        """
        ax.step(self.record.time, self.record.number_of_concurent_positions, color='black', where='mid')
        ax.set_ylabel("Number of open positions")

    @_pre_plot
    def plot_prices(self, ax: Optional[plt.Axes] = None) -> plt.Axes:
        """
        Plot the market bid and ask prices over time.

        Parameters
        ----------
        show : bool, default=True
            Show the plot after creation.
        figure_size : tuple, default=(12, 4)
            Size of the figure in inches.
        ax : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.
        save_as : str, optional
            If provided, save the figure to this path.

        Returns
        -------
        ax : matplotlib.axes.Axes
            The axes with the market prices plot.
        """
        ax.plot(self.dates, self.market.ask.open, label="Ask-Open", color='C0')
        ax.plot(self.dates, self.market.bid.open, label="Bid-Open", color='C1')
        ax.ticklabel_format(style='plain', axis='y')  # Prevent y-axis offset
        # Legend (bottom plot only)
        ax.legend(loc='upper left')
        ax.set_ylabel("Prices")


    def plot(self, *plot_type) -> plt.Figure:
        """
        Plot the portfolio's performance, including equity, capital at risk, capital,
        number of open positions, and market prices.

        Returns
        -------
        None
        """
        if len(plot_type) == 0:
            plot_type = ("equity", "capital_at_risk", "capital", "number_of_positions", "prices")
        else:
            plot_type = plot_type[0] if isinstance(plot_type[0], tuple) else plot_type

        if not isinstance(plot_type, tuple):
            plot_type = (plot_type,)

        n_plots = len(plot_type)

        with plt.style.context(mps):
            _, axs = plt.subplots(nrows=n_plots, ncols=1, figsize=(12, 2 * n_plots), sharex=True)

            plot_methods = {
                "equity": self.plot_equity,
                "capital_at_risk": self.plot_capital_at_risk,
                "capital": self.plot_capital,
                "number_of_positions": self.plot_number_of_positions,
                "prices": self.plot_prices
            }

            for ax, plot in zip(axs, plot_type):
                plot_methods[plot](ax=ax, show=False)

            plt.tight_layout()
            plt.show()

