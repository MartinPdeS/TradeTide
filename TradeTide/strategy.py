from TradeTide.tools import get_crossings
import matplotlib.pyplot as plt
import pandas
import numpy
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

    @property
    def values_0(self):
        return self.dataframe[self.metric_0.__repr__()]

    @property
    def values_1(self):
        return self.dataframe[self.metric_1.__repr__()]

    def back_test(
            self,
            stop_loss: float = 0.001,  # 0.1% loss
            take_profit: float = 0.001,  # 0.1% profit
            buy_unit: float = 1_000,
            initial_capital: float = 100_000,
            return_extra_data: bool = False) -> pandas.DataFrame:

        data = self.dataframe.copy()
        data['signal'] = numpy.where(self.metric_0.values > self.metric_1.values, 1, 0)

        # Calculate the price at which each position is taken
        data['entry price'] = data['close'].where(data['signal'].diff() == 1.0)

        # Forward fill the entry prices for the holding period of each position
        data['entry price'] = data['entry price'].ffill()

        # Calculate stop-loss and take-projet prices based on the entry prices
        data['stop loss price'] = data['entry price'] * (1 - stop_loss)
        data['take profit price'] = data['entry price'] * (1 + take_profit)

        # Determin edays where the stop-loss or take-profit is triggered
        # Stop-loss trigger: where the low is below the stop-loss price
        # Take-profit trigger: where the high is above the take-profit price
        data['stop loss triggered'] = data['low'] < data['stop loss price']
        data['take profit triggered'] = data['high'] > data['take profit price']

        # If either stop-loss or take-profit is triggered, the position should be closed
        data['close position'] = data['stop loss triggered'] | data['take profit triggered']

        # Reset the signal on the days where the position is closed due to stop-loss or take-profit
        data['signal'] = numpy.where(data['close position'], 0, data['signal'])

        # Recalculate the positions after considering stop-loss take-profit
        data['positions'] = data['signal'].diff()

        portfolio = pandas.DataFrame(index=data.index)

        portfolio['holdings'] = data['positions'].cumsum() * data['close'] * buy_unit

        portfolio['cash'] = initial_capital - (data['positions'] * data['close'] * buy_unit).cumsum()

        portfolio['total'] = portfolio['cash'] + portfolio['holdings']

        portfolio['returns'] = portfolio['total'].pct_change()

        portfolio['date'] = data['date']

        if return_extra_data:
            return portfolio, data

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
