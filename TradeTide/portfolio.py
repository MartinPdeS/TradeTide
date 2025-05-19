from TradeTide.binary.interface_portfolio import Portfolio as binding
import matplotlib.pyplot as plt

from MPSPlots.styles import mps

class Portfolio(binding):
    def plot(self, show: bool = True) -> None:
        """
        Plot the portfolio performance over time.
        """

        position_count = self.open_position_count_over_time()
        position_dates = self.get_market_dates()
        equity = self.get_equity_over_time()

        with plt.style.context(mps):
            figure, ax = plt.subplots(nrows=2, ncols=1, figsize=(10, 5))

            # Plot open position count
            ax[0].plot(position_dates, position_count, label='Open Positions')

            ax[1].plot(position_dates, equity, label='Equity', color='green')

        if show:
            plt.show()

        return figure

