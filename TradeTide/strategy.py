from TradeTide.tools import get_crossings
import matplotlib.pyplot as plt
import numpy
import pandas
from dataclasses import dataclass


@dataclass
class Strategy():
    dataframe: pandas.DataFrame
    metric_0: object
    metric_1: object
    column: str
    high_boundary: float = 1
    low_boundary: float = 1

    def __post_init__(self):
        self.metric_0.add_to_dataframe(self.dataframe, self.column)

        self.metric_1.add_to_dataframe(self.dataframe, self.column)

        self.dataframe['buy signal'] = get_crossings(self.metric_0, self.metric_1)

        self.dataframe['sell signal'] = get_crossings(self.metric_1, self.metric_0)

    @property
    def values_0(self):
        return self.dataframe[self.metric_0.__repr__()]

    @property
    def values_1(self):
        return self.dataframe[self.metric_1.__repr__()]

    def test(self) -> pandas.DataFrame:
        initial_capital: float = 100_000

        close_value = self.dataframe['close']

        positions = pandas.DataFrame(index=self.dataframe.index).fillna(0.0)

        positions['forex'] = 1_000 * self.dataframe['buy signal']

        portfolio = positions.multiply(close_value, axis=0)

        portfolio['cash'] = initial_capital - (positions['forex'].diff() * close_value).cumsum()

        portfolio['total'] = portfolio['cash'] + positions.multiply(close_value, axis=0).sum(axis=1)

        portfolio['revenue'] = portfolio['total'].pct_change()

        portfolio['date'] = self.dataframe['date']

        return portfolio

    def plot(self) -> None:
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
            zorder=-1,
            label='buy signal'
        )

        sub = dataframe.loc[dataframe['sell signal'] == True]

        sub.plot.scatter(
            ax=ax,
            x='date',
            y=self.metric_0.__repr__(),
            color='red',
            s=40,
            zorder=-1,
            label='sell signal'
        )

        plt.show()

# -
