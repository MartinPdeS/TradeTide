from TradeTide.binary.interface_portfolio import Portfolio as binding
import matplotlib.pyplot as plt

from MPSPlots.styles import mps

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Portfolio(binding):
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
            fig, axes = plt.subplots(2, 1, figsize=figsize, sharex=True)
            ax_equity, ax_count = axes[1], axes[0]

            # Format time axis
            ax_equity.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax_equity.xaxis.set_major_locator(mdates.AutoDateLocator())

            # Plot Open Position Count
            ax_count.step(self.dates, self.open_positions_count, label="Open Positions", where='post', color='blue')
            ax_count.set_ylabel("Open Positions")
            ax_count.set_title("Open Position Count Over Time")
            ax_count.grid(True)
            ax_count.ticklabel_format(style='plain', axis='y')  # Prevent y-axis offset

            # Plot Equity
            ax_equity.plot(self.dates, self.equity, label="Equity", color='green')
            ax_equity.set_ylabel("Equity")
            ax_equity.set_title("Equity Curve")
            ax_equity.set_xlabel("Date")
            ax_equity.grid(True)
            ax_equity.ticklabel_format(style='plain', axis='y')  # Prevent y-axis offset

            # Legend (bottom plot only)
            ax_equity.legend(loc='upper left')
            ax_count.legend(loc='upper left')

            fig.tight_layout()

            if save_path:
                fig.savefig(save_path, bbox_inches='tight')

            if show:
                plt.show()

            return fig

