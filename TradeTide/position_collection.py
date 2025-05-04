from TradeTide.binary import interface_position_collection
from MPSPlots.styles import mps

import matplotlib.pyplot as plt


class PositionCollection(interface_position_collection.PositionCollection):
    pass


    def run(self) -> None:
        self.open_positions()
        self.close_positions()
        self.terminate_open_positions()

    def plot(self, figsize: tuple = (12, 4)) -> None:
        market = self.get_market()

        with plt.style.context(mps):
            figure, ax = plt.subplots(1, 1, figsize=figsize)

            ax.plot(market.dates, market.ask.close, label='ask')
            ax.plot(market.dates, market.bid.close, label='bid')

            ax.set_xlabel('Date')
            ax.set_ylabel('Close price')

            for idx in range(3):
                position = self[idx]

                ax.fill_between(
                    [position.start_date, position.close_date],
                    y1=0,
                    y2=1,
                    transform=ax.get_xaxis_transform(),
                    color=f'C0',
                    alpha=0.3,
                    edgecolor='black'
                )

            ax.legend()
        plt.show()