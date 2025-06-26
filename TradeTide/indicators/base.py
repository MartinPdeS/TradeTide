import numpy as np
from MPSPlots.styles import mps as plot_style
import matplotlib.pyplot as plt

class BaseIndicator:
    def _pre_plot(function):
        def wrapper(self, show_ask: bool = True, show_bid: bool = True, show: bool = True, **kwargs):

            with plt.style.context(plot_style):
                figure, ax = plt.subplots(ncols=1, nrows=1)

                self.market.plot(ax=ax, show_ask=show_ask, show_bid=show_bid, show=False)

                function(self, ax=ax, **kwargs)
                ax.legend()

                ax.set_xlabel("Time")

                regions = np.asarray(self._cpp_regions)

                ax.fill_between(
                    self.market.dates,
                    0,
                    1,
                    where=regions == 1,
                    step='mid',
                    color='green',
                    alpha=0.2,
                    label='Market Range',
                    transform=ax.get_xaxis_transform(),
                )

                ax.fill_between(
                    self.market.dates,
                    0,
                    1,
                    where=regions == -1,
                    step='mid',
                    color='red',
                    alpha=0.2,
                    label='Market Range',
                    transform=ax.get_xaxis_transform(),
                )

                plt.tight_layout()
                if show:
                    plt.show()

            return figure, ax
        return wrapper