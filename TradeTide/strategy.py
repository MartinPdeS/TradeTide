import pandas
import numpy
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from typing import NoReturn
import matplotlib

__all__ = [
    'Custom',
    'Random',
    'MovingAverageCrossing',
    'RelativeStrengthIndex',
    'BollingerBands'
]


class BaseStrategy(ABC):
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


class Custom(BaseStrategy):
    def __init__(self, custom_signal: numpy.ndarray):
        self.custom_signal = custom_signal

    @BaseStrategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        assert len(dataframe) == len(self.custom_signal), 'Mismatch between the custom signal and dataframe'

        self.data['signal'] = self.custom_signal


class Random(BaseStrategy):
    """
    Implements a Random trading strategy as an extension of the BaseStrategy class.

    This strategy randomly generates a specified number of buy signals (represented as '1') within the trading data.
    It does not follow any financial analysis or market trend and is purely stochastic, serving more as a benchmark or
    for educational purposes rather than a practical trading strategy.

    Attributes:
        number_of_occurence (int): The total number of positive (buy) signals to generate randomly throughout the trading data.

    Methods:
        add_to_ax: Sets the label for the y-axis on a given Matplotlib axis to indicate the use of a random strategy.
        generate_signal: Randomly generates buy signals within the trading data.
    """

    def __init__(self, number_of_occurence: int = 1):
        """
        Initializes a new instance of the Random strategy with a specified number of buy signals to be randomly placed.

        Parameters:
            number_of_occurence (int): The total number of buy signals to be randomly generated. Default is 1.
        """
        self.number_of_occurence = number_of_occurence

    def add_to_ax(self, ax: matplotlib.axes.Axes) -> NoReturn:
        """
        Updates the y-axis label of the given Matplotlib axis to indicate that a random signal strategy is being used.

        This method does not plot any data as the strategy does not produce a continuous metric or indicator.

        Parameters:
            ax (matplotlib.axes.Axes): The Matplotlib axis object to update.
        """
        ax.set_ylabel('Random signal: no metric')

    @BaseStrategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        """
        Generates random buy signals within the given DataFrame based on the specified number of occurrences.

        This method creates a 'signal' column in a new DataFrame, with '1' indicating a buy signal at randomly selected indices,
        and '0' elsewhere.

        Parameters:
            dataframe (pandas.DataFrame): The input DataFrame based on which the length of the trading data is determined.

        Returns:
            pandas.DataFrame: A new DataFrame with the same index as the input DataFrame and a 'signal' column containing randomly
                              placed buy signals.
        """
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


class MovingAverageCrossing(BaseStrategy):
    """
    Implements a Moving Average Crossing strategy as an extension of the BaseStrategy class.

    This strategy involves two moving averages of a series: a "short" and a "long" moving average. A typical trading signal
    is generated when the short moving average crosses above (bullish signal) or below (bearish signal) the long moving average.
    The strategy is commonly used to identify the momentum and direction of a trend.

    Attributes:
        short_window (int): The window size of the short moving average.
        long_window (int): The window size of the long moving average.
        min_period (int): The minimum number of observations in the window required to have a value (otherwise result is NA).
        value_type (str): The type of price data to use for the moving average calculation. Typically one of ['high', 'low', 'open', 'close'].

    Methods:
        add_to_ax: Plots the short and long moving averages on a given Matplotlib axis.
    """
    def __init__(
            self,
            short_window: int = 30,
            long_window: int = 150,
            min_period: int = 10,
            value_type: str = 'close'):
        """
        Initializes a new instance of the MovingAverageCrossing strategy with specified parameters.

        Parameters:
            short_window (int): Number of periods to use for the short moving average. Default is 30.
            long_window (int): Number of periods to use for the long moving average. Default is 150.
            min_period (int): Minimum number of observations in the window required to perform the operation. Default is 10.
            value_type (str): The type of price to be used in the moving average calculation. Default is 'close'.
        """

        self.short_window = short_window
        self.long_window = long_window
        self.min_period = min_period
        self.value_type = value_type

    def add_to_ax(self, ax: matplotlib.axes.Axes) -> NoReturn:
        """
        Adds the short and long moving average plots to the specified Matplotlib axis.

        This method visualizes the short and long moving averages on a plot, which is useful for identifying potential
        crossover points that might indicate trading signals.

        Parameters:
            ax (matplotlib.axes.Axes): The Matplotlib axis object where the moving averages will be plotted.
        """
        ax.plot(
            self.data.date,
            self.data['short_window_array'],
            linewidth=2,
            label='long window'
        )

        ax.plot(
            self.data.date,
            self.data['long_window_array'],
            label='short window',
            linewidth=2,
        )
        ax.set_ylabel('SMA crossing')

    @BaseStrategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        """
        Generates trading signals based on the crossover of short-term and long-term moving averages.

        This method applies a rolling mean calculation to a specified column (`self.value_type`) in the input DataFrame,
        creating two new columns: 'long_window_array' and 'short_window_array', representing the long-term and short-term
        moving averages, respectively. A trading signal is generated when the short-term moving average crosses above the
        long-term moving average, indicated by a value of 1 in the 'signal' column; otherwise, the 'signal' value is set to 0.

        The method is decorated with `@BaseStrategy.post_generate_signal`, suggesting it may perform additional operations
        or checks defined in the `BaseStrategy` class after the signal generation.

        Parameters:
            dataframe (pandas.DataFrame): The input DataFrame containing market data. It must include a column named
                                          as specified by `self.value_type`, which is used for calculating moving averages.

        Returns:
            pandas.DataFrame: The original DataFrame is modified in-place to include three new columns:
                              'long_window_array', 'short_window_array', and 'signal'. The 'signal' column contains
                              the generated trading signals based on the moving average crossover strategy.
        """
        self.data['long_window_array'] = dataframe[self.value_type].rolling(
            window=self.long_window,
            min_periods=self.min_period
        ).mean(engine='numba')

        self.data['short_window_array'] = dataframe[self.value_type].rolling(
            window=self.short_window,
            min_periods=self.min_period
        ).mean(engine='numba')

        self.data['signal'] = numpy.where(self.data['short_window_array'] > self.data['long_window_array'], 1, 0)


class RelativeStrengthIndex(BaseStrategy):
    """
    Implements the Relative Strength Index (RSI) trading strategy as an extension of the BaseStrategy class.

    The RSI is a momentum oscillator that measures the speed and change of price movements. It oscillates between 0 and 100.
    Traditionally, the RSI is considered overbought when above 70 and oversold when below 30. Signals can be generated from
    these conditions to suggest potential buy or sell opportunities.

    Attributes:
        period (int): The number of periods used to calculate the RSI. Commonly set to 14.
        overbought_threshold (int): The RSI level above which the asset is considered overbought. Typically set to 70.
        oversold_threshold (int): The RSI level below which the asset is considered oversold. Typically set to 30.
        value_type (str): The column name from the input DataFrame on which the RSI calculation is based. Usually set to 'close'.

    Methods:
        add_to_ax: Plots the RSI and its thresholds on a given Matplotlib axis.
        generate_signal: Calculates the RSI values based on price changes and generates buy/sell signals.
    """

    def __init__(
            self,
            period: int = 14,
            overbought_threshold: int = 70,
            oversold_threshold: int = 30,
            value_type: str = 'close'):
        """
        Initializes a new instance of the RelativeStrengthIndex strategy with specified parameters.

        Parameters:
            period (int): The lookback period for RSI calculation. Default is 14.
            overbought_threshold (int): The RSI value above which the market is considered overbought. Default is 70.
            oversold_threshold (int): The RSI value below which the market is considered oversold. Default is 30.
            value_type (str): The type of price to be used in RSI calculation (e.g., 'close', 'open'). Default is 'close'.
        """
        self.period = period
        self.overbought_threshold = overbought_threshold
        self.oversold_threshold = oversold_threshold
        self.value_type = value_type

    def add_to_ax(self, ax: matplotlib.axes.Axes) -> NoReturn:
        """
        Adds the RSI plot to the specified Matplotlib axis, including the overbought and oversold threshold lines.

        Parameters:
            ax (matplotlib.axes.Axes): The Matplotlib axis object where the RSI plot will be added.
        """
        ax.plot(
            self.data.date,
            self.data['rsi'],
            label='RSI',
            linewidth=2,
            color='grey'
        )

        ax.axhline(self.overbought_threshold, linestyle='--', color='red', alpha=0.5, linewidth=2)
        ax.axhline(self.oversold_threshold, linestyle='--', color='green', alpha=0.5, linewidth=2)
        ax.set_ylabel('RSI')

    @BaseStrategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        """
        Calculates the RSI based on the provided DataFrame and generates buy or sell signals.

        A buy signal is generated when the RSI crosses below the oversold threshold, and a sell signal is generated
        when the RSI crosses above the overbought threshold. The signals are added to the 'signal' column in the DataFrame.

        Parameters:
            dataframe (pandas.DataFrame): The input DataFrame containing price data and a column specified by `value_type`.

        Returns:
            pandas.DataFrame: The input DataFrame with an added 'rsi' column containing the RSI values and a 'signal' column
                              containing the buy/sell signals.
        """
        delta = dataframe[self.value_type].diff()

        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()

        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()

        rs = gain / loss

        self.data['rsi'] = 100 - (100 / (1 + rs))

        self.data['signal'] = 0

        self.data.loc[self.data['rsi'] < self.oversold_threshold, 'signal'] = 1
        self.data.loc[self.data['rsi'] > self.overbought_threshold, 'signal'] = -1


class BollingerBands(BaseStrategy):
    """
    Implements the Bollinger Bands trading strategy as an extension of the BaseStrategy class.

    Bollinger Bands consist of a middle band being an N-period simple moving average (SMA), an upper band at K times an N-period
    standard deviation above the middle band, and a lower band at K times an N-period standard deviation below the middle band.
    These bands are used to determine overbought and oversold conditions in a market.

    Attributes:
        periods (int): The number of periods used to calculate the SMA and standard deviation.
        deviation (float): The number of standard deviations away from the SMA the upper and lower bands should be set.
        value_type (str): The column name from the input DataFrame on which the Bollinger Bands calculation is based, usually 'close'.

    Methods:
        add_to_ax: Plots the Bollinger Bands on a given Matplotlib axis.
        generate_signal: Calculates the Bollinger Bands based on price movements and generates buy/sell signals.
    """

    def __init__(
            self,
            periods: int = 20,
            deviation: float = 2,
            value_type: str = 'close'):
        """
        Initializes a new instance of the BollingerBands strategy with specified parameters.

        Parameters:
            periods (int): The lookback period for calculating the moving average and standard deviation. Default is 20.
            deviation (float): The number of standard deviations to set the upper and lower bands from the moving average. Default is 2.
            value_type (str): The type of price to be used in Bollinger Bands calculation (e.g., 'close', 'open'). Default is 'close'.
        """
        self.periods = periods
        self.deviation = deviation
        self.value_type = value_type

    def add_to_ax(self, ax: matplotlib.axes.Axes) -> NoReturn:
        """
        Adds the Bollinger Bands plot to the specified Matplotlib axis.

        This method plots the upper and lower bands of the Bollinger Bands strategy, providing a visual representation
        of the market's overbought and oversold conditions.

        Parameters:
            ax (matplotlib.axes.Axes): The Matplotlib axis object where the Bollinger Bands plot will be added.
        """
        ax.plot(
            self.data.date,
            self.data['upper_band'],
            label='upper band',
            linewidth=2,
        )

        ax.plot(
            self.data.date,
            self.data['lower_band'],
            label='lower band',
            linewidth=2,
        )
        ax.set_ylabel('Bolliner Bands strategy')

    @BaseStrategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        """
        Calculates the Bollinger Bands based on the provided DataFrame and generates buy or sell signals.

        Buy signals are generated when the price crosses below the lower band, indicating a potential oversold condition.
        Sell signals are generated when the price crosses above the upper band, indicating a potential overbought condition.
        These signals are added to a 'signal' column in the DataFrame.

        Parameters:
            dataframe (pandas.DataFrame): The input DataFrame containing price data and a column specified by `value_type`.

        Returns:
            pandas.DataFrame: The input DataFrame with added columns for the moving average ('NA'), standard deviation ('STD'),
                              upper band ('upper_band'), lower band ('lower_band'), and buy/sell signals ('signal').
        """
        self.data['NA'] = dataframe[self.value_type].rolling(window=self.periods).mean()

        self.data['STD'] = dataframe[self.value_type].rolling(window=self.periods).std()

        self.data['upper_band'] = self.data['NA'] + (self.data['STD'] * self.deviation)

        self.data['lower_band'] = self.data['NA'] - (self.data['STD'] * self.deviation)

        # Generate buy signal when the close price crosses below the lower band
        self.data['signal'] = numpy.where(dataframe['close'] < self.data['lower_band'], 1, 0)

        # Generate sell signal when the close price corsses above the upper band
        self.data['signal'] = numpy.where(dataframe['close'] > self.data['lower_band'], -1, self.data['signal'])
# -
