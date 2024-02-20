import pandas
import numpy
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt


class Strategy(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def generate_signal(self) -> pandas.DataFrame:
        pass

    def plot(self):
        self.signal.plot.scatter(x='date', y='value')

        plt.show()


class MovingAverageCrossing(Strategy):

    def __init__(
            self,
            short_window: int = 30,
            long_window: int = 150,
            min_period: int = 10,
            value_type: str = 'close'):
        """
        Constructs a new instance.

        :param      short_window:  The short window for the SMA
        :type       short_window:  int
        :param      long_window:   The long window for the SMA
        :type       long_window:   int
        :param      min_period:    The minimum period
        :type       min_period:    int
        :param      value_type:    The value type ['high', 'low', 'open', 'close']
        :type       value_type:    str
        """
        self.short_window = short_window
        self.long_window = long_window
        self.min_period = min_period
        self.value_type = value_type

    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        self.signal = pandas.DataFrame(index=dataframe.index)

        long_window_array = dataframe[self.value_type].rolling(
            window=self.long_window,
            min_periods=self.min_period
        ).mean(engine='numba')

        short_window_array = dataframe[self.value_type].rolling(
            window=self.short_window,
            min_periods=self.min_period
        ).mean(engine='numba')

        self.signal['value'] = numpy.where(short_window_array > long_window_array, 1, 0)

        self.signal['date'] = dataframe['date']

        return self.signal


class RelativeStrengthIndex(Strategy):
    def __init__(
            self,
            period: int = 14,
            overbought_threshold: int = 70,
            oversold_threshold: int = 30,
            value_type: str = 'close'):
        """
        Constructs a new instance.

        :param      period:                The number of period used to compute the RSI
        :type       period:                int
        :param      overbought_threshold:  The RSI threshold above which the market is considered overbought, and a sell signal may be generated
        :type       overbought_threshold:  int
        :param      oversold_threshold:    The RSI threshold below which the market is considered oversold, and a buy signal may be generated.
        :type       oversold_threshold:    int
        :param      value_type:            The value type
        :type       value_type:            str
        """
        self.period = period
        self.overbought_threshold = overbought_threshold
        self.oversold_threshold = oversold_threshold
        self.value_type = value_type

    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        self.signal = pandas.DataFrame(index=dataframe.index)

        delta = dataframe[self.value_type].diff()

        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()

        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()

        rs = gain / loss

        rsi = 100 - (100 / (1 + rs))

        self.signal['value'] = 0

        self.signal.loc[rsi < self.oversold_threshold, 'value'] = 1
        self.signal.loc[rsi > self.overbought_threshold, 'value'] = -1

        self.signal['date'] = dataframe['date']

        return self.signal


class BollingerBands(Strategy):
    def __init__(
            self,
            periods: int = 20,
            deviation: float = 2,
            value_type: str = 'close'):
        """
        Constructs a new instance.

        :param      periods:     The number of period for the moving average
        :type       periods:     int
        :param      deviation:   The number of standard deviation for the upper and lower bands
        :type       deviation:   float
        :param      value_type:  The value type
        :type       value_type:  str
        """
        self.periods = periods
        self.deviation = deviation
        self.value_type = value_type

    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        self.signal = pandas.DataFrame(index=dataframe.index)

        self.signal['date'] = dataframe['date']

        self.signal['NA'] = dataframe[self.value_type].rolling(window=self.periods).mean()

        self.signal['STD'] = dataframe[self.value_type].rolling(window=self.periods).std()

        self.signal['upper_band'] = self.signal['NA'] + (self.signal['STD'] * self.deviation)

        self.signal['lower_band'] = self.signal['NA'] - (self.signal['STD'] * self.deviation)

        # Generate buy signal when the close price crosses below the lower band
        self.signal['value'] = numpy.where(dataframe['close'] < self.data['lower_band'], 1, 0)

        # Generate sell signal when the close price corsses above the upper band
        self.signal['value'] = numpy.where(dataframe['close'] > self.data['lower_band'], -1, self.signal['value'])


# -
