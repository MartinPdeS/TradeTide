import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from typing import Tuple, Union, Optional

from TradeTide.binary.interface_position_collection import PositionCollection
from TradeTide import position

from MPSPlots.styles import mps
import matplotlib.pyplot as plt

Long = position.Long
Short = position.Short

class PositionCollection(PositionCollection):

    def plot(
        self,
        figsize: Tuple[int, int] = (12, 4),
        max_positions: Union[int, float] = np.inf,
        ax: Optional[plt.Axes] = None
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

            fig, (ax_long, ax_short) = plt.subplots(nrows=2, ncols=1, figsize=figsize, sharex=True, sharey=True)
            ax_short.set_xlabel("Date")
            ax_long.set_ylabel(f"Bid Price")
            ax_short.set_ylabel(f"Ask Price")

            market = self.get_market()

            # 2) Define colors
            ask_color   = "#1f77b4"
            bid_color   = "#ff7f0e"

            # 3) Plot ask/bid series
            ln_bid, = ax_long.plot(market.dates, market.bid.open, label="Bid", color=bid_color, linewidth=1.5)
            ax_long.fill_between(market.dates, market.bid.low, market.bid.high, linestyle='--', color='black', linewidth=1, alpha=0.2)

            ln_ask, = ax_short.plot(market.dates, market.ask.open, label="Ask", color=ask_color, linewidth=1.5)
            ax_short.fill_between(market.dates, market.ask.low, market.ask.high, linestyle='--', color='black', linewidth=1,  alpha=0.2)

            # 4) Shade and overlay for closed positions
            drawn = 0

            for idx in range(min(len(self), max_positions)):

                position = self[idx]

                ax = ax_long if position.is_long else ax_short

                start, end = position.start_date, position.close_date
                fill_color = "C0" if position.is_long else "C1"

                # shade the region
                ax.axvspan(start, end, facecolor=fill_color, edgecolor="black", alpha=0.2)

                # SL and TP lines
                ax.plot(
                    position.exit_strategy.dates,
                    position.exit_strategy.stop_loss_prices,
                    linestyle="--",
                    color="red",
                    linewidth=1,
                )

                ax.plot(
                    position.exit_strategy.dates,
                    position.exit_strategy.take_profit_prices,
                    linestyle="--",
                    color="green",
                    linewidth=1,
                )

                drawn += 1
                if drawn >= max_positions:
                    break

            # 5) Custom legend
            legend_handles_long = [
                ln_bid,
                Line2D([0], [0], color="red", linestyle="--", label="Stop Loss"),
                Line2D([0], [0], color="green", linestyle="--", label="Take Profit"),
                Patch(facecolor="C0",  edgecolor="none", label="Long Position"),
            ]
            ax_long.legend(handles=legend_handles_long, loc="upper left", framealpha=0.9)

            legend_handles_short = [
                ln_ask,
                Line2D([0], [0], color="red", linestyle="--", label="Stop Loss"),
                Line2D([0], [0], color="green", linestyle="--", label="Take Profit"),
                Patch(facecolor="C1", edgecolor="none", label="Short Position"),
            ]
            ax_short.legend(handles=legend_handles_short, loc="upper left", framealpha=0.9)

            fig.autofmt_xdate()
            fig.tight_layout()
            plt.show()

        return fig, ax
