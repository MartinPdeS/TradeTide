import matplotlib.pyplot as plt
import pandas
import numpy
from dataclasses import dataclass


@dataclass
class BackTester():
    dataframe: pandas.DataFrame
    signal: pandas.DataFrame

    def __post_init__(self):
        pass

    @property
    def values_0(self):
        return self.dataframe[self.metric_0.__repr__()]

    @property
    def values_1(self):
        return self.dataframe[self.metric_1.__repr__()]

    def back_test(
            self,
            stop_loss: float = 0.01,
            take_profit: float = 0.01,
            buy_unit: float = 1_000,
            initial_capital: float = 100_000,
            return_extra_data: bool = False) -> pandas.DataFrame:
        """
        Run the back tests on the data

        :param      stop_loss:          The stop loss threshold [default is 1%]
        :type       stop_loss:          float
        :param      take_profit:        The take profit threshold [default is 1%]
        :type       take_profit:        float
        :param      buy_unit:           The buy unit
        :type       buy_unit:           float
        :param      initial_capital:    The initial capital
        :type       initial_capital:    float
        :param      return_extra_data:  If true returns some extra data on the computation as a dataframe
        :type       return_extra_data:  bool

        :returns:   The computed portfolio
        :rtype:     pandas.DataFrame
        """

        data = self.dataframe.copy()
        data['signal'] = self.signal['value']

        # Calculate the price at which each position is taken
        data['entry price'] = data['close'].where(data['signal'].diff() == 1.0)

        # Forward fill the entry prices for the holding period of each position
        data['entry price'] = data['entry price'].ffill()

        # Calculate stop-loss and take-projet prices based on the entry prices
        data['stop loss price'] = data['entry price'] * (1 - stop_loss)
        data['take profit price'] = data['entry price'] * (1 + take_profit)

        # Determine days where the stop-loss or take-profit is triggered
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

        self.data = data
        self.portfolio = portfolio

        if return_extra_data:
            return portfolio, data

        return portfolio

    def plot(
            self,
            show_stop_loss: bool = False,
            show_take_win: bool = False,
            show_holdings: bool = False,
            show_totals: bool = False,
            show_cash: bool = False) -> None:

        meta_data = self.data.copy()

        ax = meta_data.plot.scatter(
            x='date',
            y='signal',
            figsize=(12, 4),
            label='signal',
            color='C0'
        )

        ax_right = ax.twinx()

        if show_stop_loss:
            meta_data['stop loss triggered'] = meta_data['stop loss triggered'].astype(float)

            meta_data.plot.scatter(
                ax=ax,
                x='date',
                y='stop loss triggered',
                label='stop-loss triger',
                color='red',
                marker=7,

            )

        if show_take_win:
            meta_data['take profit triggered'] = meta_data['take profit triggered'].astype(float)

            meta_data.plot.scatter(
                ax=ax,
                x='date',
                y='take profit triggered',
                label='take profit triger',
                color='green',
                marker=6,
            )

        if show_holdings:
            self.portfolio.plot(
                x='date',
                y='holdings',
                linewidth=2,
                ax=ax_right
            )

        if show_totals:
            self.portfolio.plot(
                x='date',
                y='total',
                linewidth=2,
                ax=ax_right
            )

        if show_cash:
            self.portfolio.plot(
                x='date',
                y='cash',
                linewidth=2,
                ax=ax_right
            )

        ax.legend(loc=2)
        ax_right.legend(loc=1)

        plt.show()

# -
