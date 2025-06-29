import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Union, Optional

from TradeTide.binary.interface_position_collection import PositionCollection
from TradeTide import position
import TradeTide

from MPSPlots.styles import mps
import matplotlib.pyplot as plt

Long = position.Long
Short = position.Short

class PositionCollection(PositionCollection):

    def __init__(self, market, trade_signal: np.ndarray, debug_mode: bool = False):
        """
        Initialize the PositionCollection with a market and trade signal.

        Parameters
        ----------
        market : Market
            The market data to use for positions.
        trade_signal : np.ndarray
            The trade signal to use for opening positions.
        """
        self.market = market
        super().__init__(
            market=market,
            trade_signal=trade_signal,
            debug_mode=TradeTide.debug_mode if TradeTide.debug_mode else debug_mode
            )

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
            self.market.plot_ask(ax=ax_short, show=False)

            self.market.plot_bid(ax=ax_long, show=False)

            ax_short.set_xlabel("Date")
            ax_long.set_ylabel(f"Bid Price")
            ax_short.set_ylabel(f"Ask Price")

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

            fig.autofmt_xdate()
            fig.tight_layout()
            plt.show()

        return fig, ax
