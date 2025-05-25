from typing import Tuple, Optional, Union
import numpy as np

from TradeTide import position
from TradeTide.binary.interface_portfolio import Portfolio as binding
import matplotlib.pyplot as plt
from MPSPlots.styles import mps
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

Long = position.Long
Short = position.Short


class Portfolio(binding):
    def plot_positions(
        self,
        figsize: Tuple[int, int] = (12, 4),
        max_positions: Union[int, float] = np.inf,
        price_type: str = "close",
        show: bool = False
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Plot market bid/ask prices and shade closed positions, using the mps style,
        consistent naming of 'position', and a clear legend with distinct colors.

        Parameters
        ----------
        figsize : tuple[int, int], default=(12,4)
            Size of the figure in inches.
        max_positions : int or float, default=np.inf
            Maximum number of positions to draw (in chronological order).
        price_type : {'open','high','low','close'}, default='close'
            Which price series to plot.
        ax : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.

        Returns
        -------
        fig, ax : Figure and Axes objects for further customization or saving.
        """
        with plt.style.context(mps):
            # 1) Create or get axes

            fig, axes = plt.subplots(ncols=1, nrows=2, figsize=figsize, sharex=True)

            # 2) Define colors
            long_fill   = "lightblue"#(0.2, 0.8, 0.2, 0.3)
            short_fill  = (0.8, 0.2, 0.2, 0.3)
            sl_color    = "#d62728"
            tp_color    = "#2ca02c"

            # 3) Plot ask/bid series
            ln_ask, = axes[0].plot(self.dates, self.market.ask.price, label="Ask", color='C0', linewidth=1.5)
            axes[0].fill_between(self.dates, y1=self.market.ask.low, y2=self.market.ask.high, color='C0', alpha=0.2)

            ln_bid, = axes[1].plot(self.dates, self.market.bid.price, label="Bid", color='C1', linewidth=1.5)
            axes[1].fill_between(self.dates, y1=self.market.bid.low, y2=self.market.bid.high, color='C1', alpha=0.2)

            for ax in axes:
                ax.set_xlabel("Date")
                ax.set_ylabel(f"{price_type.capitalize()} Price")
                ax.grid(True, linestyle="--", alpha=0.4)

            # 4) Shade and overlay for closed positions
            drawn = 0
            # for position in self.get_all_positions(count=int(max_positions)):

            positions = self.get_positions(max_positions)

            for idx, position in enumerate(positions):
                if idx > max_positions:
                    break

                if not position.is_terminated:
                    continue

                start, end = position.start_date, position.close_date

                if isinstance(position, Long):
                    axes[0].axvspan(start, end, facecolor=long_fill, edgecolor="black", alpha=0.2)
                    axes[0].plot(position.dates(), position.stop_loss_prices(), linestyle="--", color=sl_color, linewidth=1, label="_nolegend_")
                    axes[0].plot(position.dates(), position.take_profit_prices(), linestyle="--", color=tp_color, linewidth=1, label="_nolegend_")
                else:
                    axes[1].axvspan(start, end, facecolor=short_fill, edgecolor="black", alpha=0.2)
                    axes[1].plot(position.dates(), position.stop_loss_prices(), linestyle="--", color=sl_color, linewidth=1, label="_nolegend_")
                    axes[1].plot(position.dates(), position.take_profit_prices(), linestyle="--", color=tp_color, linewidth=1, label="_nolegend_")

                drawn += 1
                if drawn >= max_positions:
                    break

            # 5) Custom legend
            legend_handles_long = [
                ln_ask,
                Line2D([0], [0], color=sl_color, linestyle="--", label="Stop Loss"),
                Line2D([0], [0], color=tp_color, linestyle="--", label="Take Profit"),
                Patch(facecolor=long_fill,  edgecolor="none", label="Long Position"),
            ]

            legend_handles_short = [
                ln_bid,
                Line2D([0], [0], color=sl_color, linestyle="--", label="Stop Loss"),
                Line2D([0], [0], color=tp_color, linestyle="--", label="Take Profit"),
                Patch(facecolor=short_fill, edgecolor="none", label="Short Position")
            ]
            axes[0].legend(handles=legend_handles_long, loc="upper left", framealpha=0.9)
            axes[1].legend(handles=legend_handles_short, loc="upper left", framealpha=0.9)

            fig.autofmt_xdate()
            fig.tight_layout()
            if show:
                plt.show()

        return fig, ax


    def _pre_plot(function):
        def wrapper(self, ax: plt.Axes = None, figsize: tuple = (12, 4), show: bool = True, **kwargs):

            if ax is None:
                with plt.style.context(mps):
                    _, ax = plt.subplots(1, 1, figsize=figsize)
                    ax.set_xlabel("Date")

            ax = function(self, ax=ax, **kwargs)

            if show:
                plt.show()

            return ax

        return wrapper


    @_pre_plot
    def plot_equity(self, ax: Optional[plt.Axes] = None, show: bool = True, figsize=(12, 4)) -> plt.Axes:
        ax.plot(self.record.time, self.record.equity, color='black')
        # ax.plot(self.state.time, self.state.capital, color='C0')
        ax.set_ylabel("Equity")

    def plot_capital_at_risk(self, ax: Optional[plt.Axes] = None, show: Optional[bool] = True, figsize=(12, 4)) -> plt.Axes:
        ax.step(self.record.time, self.record.capital_at_risk, color='black', where='mid')
        ax.set_ylabel("Capital at Risk")


    def plot_number_of_positions(self, ax: Optional[plt.Axes] = None, show: Optional[bool] = True, figsize=(12, 4)) -> plt.Axes:
        ax.step(self.record.time, self.record.number_of_concurent_positions, color='black', where='mid')
        ax.set_ylabel("# Positions")

    def plot_prices(self, ax: Optional[plt.Axes] = None, show: Optional[bool] = True, figsize=(12, 4)) -> plt.Axes:
        ax.plot(self.dates, self.market.ask.price, label="Ask", color='C0')
        ax.plot(self.dates, self.market.bid.price, label="Bid", color='C1')
        ax.ticklabel_format(style='plain', axis='y')  # Prevent y-axis offset
        # Legend (bottom plot only)
        ax.legend(loc='upper left')
        ax.set_ylabel("Prices")


    def plot(self, show: Optional[bool] = True, save_path: Optional[str] = None, figsize: Optional[tuple] = (12, 6)) -> plt.Figure:
        """
        Plot the portfolio's equity and open position count over time.

        Args:
            show (bool): Whether to display the plot (default: True).
            save_path (str): Optional file path to save the figure.
            figsize (tuple): Figure size in inches (default: (12, 6)).

        Returns:
            matplotlib.figure.Figure: The matplotlib Figure object.
        """
        with plt.style.context(mps):
            figure, axes = plt.subplots(4, 1, figsize=figsize, sharex=True)
            axes[-1].set_xlabel("Date")

            # Plot prices
            self.plot_prices(ax=axes[0], show=False)

            # Plot Open Position Count
            self.plot_number_of_positions(ax=axes[1], show=False)

            # Plot Equity
            self.plot_equity(ax=axes[2], show=False)

            # Plot Open Position Count
            self.plot_capital_at_risk(ax=axes[3], show=False)

            figure.tight_layout()

            if save_path:
                figure.savefig(save_path, bbox_inches='tight')

            if show:
                plt.show()

            return figure

