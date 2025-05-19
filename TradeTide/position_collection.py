import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from typing import Tuple, Union, Optional

from TradeTide.binary.interface_position_collection import PositionCollection
from TradeTide.binary.interface_position import Long
from MPSPlots.styles import mps

import matplotlib.pyplot as plt


class PositionCollection(PositionCollection):
    pass


    def run(self) -> None:
        self.open_positions()
        self.propagate_positions()
        self.terminate_open_positions()


    def plot(
        self,
        figsize: Tuple[int, int] = (12, 4),
        max_positions: Union[int, float] = np.inf,
        price_type: str = "close",
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
            if ax is None:
                fig, ax = plt.subplots(figsize=figsize)
            else:
                fig = ax.get_figure()

            market = self.get_market()
            dates = market.dates
            ask = getattr(market.ask, price_type)
            bid = getattr(market.bid, price_type)

            # 2) Define colors
            ask_color   = "#1f77b4"
            bid_color   = "#ff7f0e"
            long_fill   = "lightblue"#(0.2, 0.8, 0.2, 0.3)
            short_fill  = (0.8, 0.2, 0.2, 0.3)
            sl_color    = "#d62728"
            tp_color    = "#2ca02c"

            # 3) Plot ask/bid series
            ln_ask, = ax.plot(dates, ask, label="Ask", color=ask_color, linewidth=1.5)
            ln_bid, = ax.plot(dates, bid, label="Bid", color=bid_color, linewidth=1.5)

            ax.set_xlabel("Date")
            ax.set_ylabel(f"{price_type.capitalize()} Price")
            ax.grid(True, linestyle="--", alpha=0.4)

            # 4) Shade and overlay for closed positions
            drawn = 0
            # for position in self.get_all_positions(count=int(max_positions)):

            for idx in range(len(self)):
                if idx > max_positions:
                    break
                position = self[idx]

                if not position.is_closed:
                    continue

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
            plt.show()

        return fig, ax
