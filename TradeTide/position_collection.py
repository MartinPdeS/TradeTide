import numpy

from TradeTide.binary import interface_position_collection
from MPSPlots.styles import mps

import matplotlib.pyplot as plt


class PositionCollection(interface_position_collection.PositionCollection):
    pass


    def run(self) -> None:
        self.open_positions()
        self.close_positions()
        self.terminate_open_positions()

    def plot(self, figsize: tuple = (12, 4), max_number_of_position: int = numpy.inf) -> None:
        market = self.get_market()

        with plt.style.context(mps):
            figure, ax = plt.subplots(1, 1, figsize=figsize)

            ax.plot(market.dates, market.ask.close, label='ask')
            ax.plot(market.dates, market.bid.close, label='bid')

            ax.set_xlabel('Date')
            ax.set_ylabel('Close price')

            for idx in range(min(max_number_of_position, len(self))):

                position = self[idx]

                if not position.is_closed:
                    continue

                ax.fill_between(
                    [position.start_date, position.close_date],
                    y1=0,
                    y2=1,
                    transform=ax.get_xaxis_transform(),
                    color='green' if isinstance(position, interface_position_collection.Long) else 'red',
                    alpha=0.3,
                    edgecolor='black'
                )

            ax.legend()
        plt.show()