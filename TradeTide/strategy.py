import pandas
import numpy
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt

__all__ = [
    'Custom',
    'Random',
    'MovingAverageCrossing',
    'RelativeStrengthIndex',
    'BollingerBands'
]


class Strategy(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def generate_signal(self) -> pandas.DataFrame:
        pass

    def plot(self):
        self.data.plot.scatter(x='date', y='signal')

        plt.show()

    @property
    def signal(self) -> pandas.Series:
        return self.data['signal']

    def add_to_ax(self, ax):
        pass

    def post_generate_signal(function):
        def wrapper(self, dataframe):
            self.data = pandas.DataFrame(index=dataframe.index)

            function(self, dataframe=dataframe)

            self.data['date'] = dataframe['date']

            return self.data['signal']

        return wrapper


class Custom(Strategy):
    def __init__(self, custom_signal: numpy.ndarray):
        self.custom_signal = custom_signal

    @Strategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        assert len(dataframe) == len(self.custom_signal), 'Mismatch between the custom signal and dataframe'

        self.data['signal'] = self.custom_signal


class Random(Strategy):
    """
    Random strategy with a given number of occurence
    """

    def __init__(self, number_of_occurence: int = 1):
        """
        Constructs a new instance.

        :param      number_of_occurence:  The number of occurence for a positive signal
        :type       number_of_occurence:  int
        """
        self.number_of_occurence = number_of_occurence

    def add_to_ax(self, ax) -> None:
        ax.set_ylabel('Random signal: no metric')

    @Strategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        random_signal = numpy.zeros(len(dataframe))

        random_index = numpy.random.choice(
            len(dataframe),
            size=self.number_of_occurence,
            replace=True,
            p=None
        )

        random_signal[random_index] = 1

        self.data = pandas.DataFrame(index=dataframe.index)

        self.data['signal'] = random_signal


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

    def add_to_ax(self, ax):
        ax.plot(
            self.data.date,
            self.data['short_window_array'],
            label='long window'
        )

        ax.plot(
            self.data.date,
            self.data['long_window_array'],
            label='short window'
        )
        ax.set_ylabel('SMA crossing')

    @Strategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:

        self.data['long_window_array'] = dataframe[self.value_type].rolling(
            window=self.long_window,
            min_periods=self.min_period
        ).mean(engine='numba')

        self.data['short_window_array'] = dataframe[self.value_type].rolling(
            window=self.short_window,
            min_periods=self.min_period
        ).mean(engine='numba')

        self.data['signal'] = numpy.where(self.data['short_window_array'] > self.data['long_window_array'], 1, 0)


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

    def add_to_ax(self, ax):
        ax.plot(
            self.data.date,
            self.data['rsi'],
            label='RSI',
            color='grey'
        )

        ax.axhline(self.overbought_threshold, linestyle='--', color='red', alpha=0.5)
        ax.axhline(self.oversold_threshold, linestyle='--', color='green', alpha=0.5)
        ax.set_ylabel('RSI')

    @Strategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        delta = dataframe[self.value_type].diff()

        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()

        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()

        rs = gain / loss

        self.data['rsi'] = 100 - (100 / (1 + rs))

        self.data['signal'] = 0

        self.data.loc[self.data['rsi'] < self.oversold_threshold, 'signal'] = 1
        self.data.loc[self.data['rsi'] > self.overbought_threshold, 'signal'] = -1


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

    def add_to_ax(self, ax: plt.axis) -> None:
        ax.plot(
            self.data.date,
            self.data['upper_band'],
            label='upper band'
        )

        ax.plot(
            self.data.date,
            self.data['lower_band'],
            label='lower band'
        )
        ax.set_ylabel('Bolliner Bands strategy')

    @Strategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        self.data['NA'] = dataframe[self.value_type].rolling(window=self.periods).mean()

        self.data['STD'] = dataframe[self.value_type].rolling(window=self.periods).std()

        self.data['upper_band'] = self.data['NA'] + (self.data['STD'] * self.deviation)

        self.data['lower_band'] = self.data['NA'] - (self.data['STD'] * self.deviation)

        # Generate buy signal when the close price crosses below the lower band
        self.data['signal'] = numpy.where(dataframe['close'] < self.data['lower_band'], 1, 0)

        # Generate sell signal when the close price corsses above the upper band
        self.data['signal'] = numpy.where(dataframe['close'] > self.data['lower_band'], -1, self.data['signal'])
# -
