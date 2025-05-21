from typing import Tuple, Optional, Union
import numpy as np

from TradeTide import position
from TradeTide.binary.interface_portfolio import Portfolio as binding
import matplotlib.pyplot as plt
from MPSPlots.styles import mps
import matplotlib.dates as mdates
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
        ax: Optional[plt.Axes] = None,
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
            if ax is None:
                fig, ax = plt.subplots(figsize=figsize)
            else:
                fig = ax.get_figure()

            # 2) Define colors
            long_fill   = "lightblue"#(0.2, 0.8, 0.2, 0.3)
            short_fill  = (0.8, 0.2, 0.2, 0.3)
            sl_color    = "#d62728"
            tp_color    = "#2ca02c"

            # 3) Plot ask/bid series
            ln_ask, = ax.plot(self.dates, self.market.ask.price, label="Ask", color='C0', linewidth=1.5)
            ax.fill_between(self.dates, y1=self.market.ask.low, y2=self.market.ask.high, color='C0', alpha=0.2)

            ln_bid, = ax.plot(self.dates, self.market.bid.price, label="Bid", color='C1', linewidth=1.5)
            ax.fill_between(self.dates, y1=self.market.bid.low, y2=self.market.bid.high, color='C1', alpha=0.2)


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

                start, end = position.start_date, position.close_date
                fill_color = long_fill if isinstance(position, Long) else short_fill

                # shade the region
                ax.axvspan(start, end, facecolor=fill_color, edgecolor="black", alpha=0.2)

                # SL and TP lines
                ax.plot(position.dates(), position.stop_loss_prices(),
                        linestyle="--", color=sl_color, linewidth=1, label="_nolegend_")
                ax.plot(position.dates(), position.take_profit_prices(),
                        linestyle="--", color=tp_color, linewidth=1, label="_nolegend_")

                drawn += 1
                if drawn >= max_positions:
                    break

            # 5) Custom legend
            legend_handles = [
                ln_ask,
                ln_bid,
                Line2D([0], [0], color=sl_color, linestyle="--", label="Stop Loss"),
                Line2D([0], [0], color=tp_color, linestyle="--", label="Take Profit"),
                Patch(facecolor=long_fill,  edgecolor="none", label="Long Position"),
                Patch(facecolor=short_fill, edgecolor="none", label="Short Position")
            ]
            ax.legend(handles=legend_handles, loc="upper left", framealpha=0.9)

            fig.autofmt_xdate()
            fig.tight_layout()
            if show:
                plt.show()

        return fig, ax


    def plot(self, show: bool = True, save_path: str = None, figsize=(12, 6)) -> plt.Figure:
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
            fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=True)

            # Plot prices
            ax = axes[0]
            ax.set_ylabel("Prices")
            ax.set_title("Market Prices Over Time")
            ax.plot(self.dates, self.market.ask.price, label="Ask", color='C0')
            ax.plot(self.dates, self.market.bid.price, label="Bid", color='C1')
            ax.ticklabel_format(style='plain', axis='y')  # Prevent y-axis offset
            # Legend (bottom plot only)
            ax.legend(loc='upper left')

            # Plot Open Position Count
            ax = axes[1]
            ax.step(self.dates, self.open_positions_count, label="Open Positions", where='post', color='blue')
            ax.set_ylabel("Open Positions")
            ax.set_title("Open Position Count Over Time")
            ax.ticklabel_format(style='plain', axis='y')  # Prevent y-axis offset
            # Legend (bottom plot only)
            ax.legend(loc='upper left')

            # Plot Equity
            ax = axes[2]
            ax.plot(self.dates, self.equity, label="Equity", color='green')
            ax.set_ylabel("Equity")
            ax.set_title("Equity Curve")
            ax.set_xlabel("Date")
            ax.ticklabel_format(style='plain', axis='y')  # Prevent y-axis offset
            # Legend (bottom plot only)
            ax.legend(loc='upper left')
            # Format time axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())



            fig.tight_layout()

            if save_path:
                fig.savefig(save_path, bbox_inches='tight')

            if show:
                plt.show()

            return fig

