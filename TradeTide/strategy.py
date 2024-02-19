from TradeTide.tools import get_crossings
import matplotlib.pyplot as plt
import numpy


class Strategy():
    def __init__(self, dataframe, metric_0, metric_1, column: str):
        self.dataframe = dataframe
        self.column = column
        self.metric_0 = metric_0
        self.metric_1 = metric_1

        self.metric_0.add_to_dataframe(dataframe, column)

        self.metric_1.add_to_dataframe(dataframe, column)

        self.dataframe['buy signal'] = get_crossings(self.metric_0, self.metric_1)

        self.dataframe['sell signal'] = get_crossings(self.metric_1, self.metric_0)

    @property
    def values_0(self):
        return self.dataframe[self.metric_0.__repr__()]

    @property
    def values_1(self):
        return self.dataframe[self.metric_1.__repr__()]

    def plot(self):
        metric_list = [
            self.metric_0.__repr__(),
            self.metric_1.__repr__()
        ]

        dataframe = self.dataframe

        ax = dataframe.plot(x='date', y=metric_list)

        sub = dataframe.loc[dataframe['buy signal'] == True]

        sub.plot.scatter(
            ax=ax,
            x='date',
            y=self.metric_0.__repr__(),
            color='green',
            s=40,
            zorder=-1
        )

        sub = dataframe.loc[dataframe['sell signal'] == True]

        sub.plot.scatter(
            ax=ax,
            x='date',
            y=self.metric_0.__repr__(),
            color='red',
            s=40,
            zorder=-1
        )

        plt.show()

# -
