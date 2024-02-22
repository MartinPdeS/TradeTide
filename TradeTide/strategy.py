import pandas
import numpy
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt

__all__ = [
    'Custom',
    'Random',
    'MovingAverageCrossing',
    'RelativeStrengthIndex',
    'BollingerBands',
    'MoneyFlowIndex',
    'IchimokuCloud'
    'VWAP',
    'MACD',
    'StochasticOscillator',
    'ROC',
    'ParabolicSAR'
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

class MoneyFlowIndex(Strategy):
    def __init__(self, period: int = 14, overbought_threshold: float = 80, oversold_threshold: float = 20):
        """
        Initializes the Money Flow Index strategy.

        :param period: The number of periods over which to calculate the MFI.
        :param overbought_threshold: The threshold above which the asset is considered overbought.
        :param oversold_threshold: The threshold below which the asset is considered oversold.
        """
        self.period = period
        self.overbought_threshold = overbought_threshold
        self.oversold_threshold = oversold_threshold

    def add_to_ax(self, ax):
        ax.plot(
            self.data.date,
            self.data['mfi'],
            label='MFI',
            color='grey'
        )

        ax.axhline(self.overbought_threshold, linestyle='--', color='red', alpha=0.5)
        ax.axhline(self.oversold_threshold, linestyle='--', color='green', alpha=0.5)
        ax.set_ylabel('mfi')

    @Strategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        # Ensure 'volume' is not empty and not constant
        assert not dataframe['volume'].empty, "Volume data is empty."
        assert dataframe['volume'].nunique() > 1, "Volume data is constant."

        # Calculate Typical Price
        typical_price = (dataframe['high'] + dataframe['low'] + dataframe['close']) / 3

        # Calculate Raw Money Flow
        raw_money_flow = typical_price * dataframe['volume']

        # Determine Positive and Negative Money Flows
        money_flow = raw_money_flow.copy()
        money_flow[1:] = numpy.where(typical_price.values[1:] > typical_price.values[:-1], raw_money_flow.values[1:], -raw_money_flow.values[1:])
        money_flow.iloc[0] = 0  # First element is not compared, set to 0

        positive_money_flow = money_flow.copy()
        negative_money_flow = money_flow.copy()

        positive_money_flow[positive_money_flow < 0] = 0
        negative_money_flow[negative_money_flow > 0] = 0
        negative_money_flow = negative_money_flow.abs()

        # Calculate Money Flow Ratio
        rolling_positive_mf = positive_money_flow.rolling(window=self.period).sum()
        rolling_negative_mf = negative_money_flow.rolling(window=self.period).sum()

        money_flow_ratio = rolling_positive_mf / rolling_negative_mf

        # Calculate Money Flow Index
        self.data['mfi'] = 100 - (100 / (1 + money_flow_ratio))

        # Generate signals based on overbought/oversold thresholds
        self.data['signal'] = 0  # Default to no signal
        self.data.loc[self.data['mfi'] < self.oversold_threshold, 'signal'] = 1  # Buy signal
        self.data.loc[self.data['mfi'] > self.overbought_threshold, 'signal'] = -1  # Sell signal

        return self.data['signal']

class IchimokuCloud(Strategy):
    def __init__(
            self,
            conversion_line_period: int = 9,
            base_line_period: int = 26,
            leading_span_b_period: int = 52,
            lagging_span_period: int = 26):
        """
        Initializes the Ichimoku Cloud strategy.

        :param conversion_line_period: The number of periods for the Conversion Line.
        :param base_line_period: The number of periods for the Base Line.
        :param leading_span_b_period: The number of periods for Leading Span B.
        :param lagging_span_period: The number of periods for the Lagging Span.
        """
        self.conversion_line_period = conversion_line_period
        self.base_line_period = base_line_period
        self.leading_span_b_period = leading_span_b_period
        self.lagging_span_period = lagging_span_period

    def add_to_ax(self, ax):
        ax.fill_between(
            self.data.date,
            self.data['leading_span_a'],
            self.data['leading_span_b'],
            where=self.data['leading_span_a'] >= self.data['leading_span_b'],
            facecolor='green',
            alpha=0.5,
            label='Kumo bullish'
        )
        ax.fill_between(
            self.data.date,
            self.data['leading_span_a'],
            self.data['leading_span_b'],
            where=self.data['leading_span_a'] < self.data['leading_span_b'],
            facecolor='red',
            alpha=0.5,
            label='Kumo bearish'
        )
        ax.plot(
            self.data.date,
            self.data['conversion_line'],
            color='blue',
            label='Conversion Line'
        )
        ax.plot(
            self.data.date,
            self.data['base_line'],
            color='orange',
            label='Base Line'
        )
        ax.set_ylabel('Ichimoku Cloud Strategy')

    @Strategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        # Calculate components of the Ichimoku Cloud
        high = dataframe['high']
        low = dataframe['low']
        close = dataframe['close']

        self.data['conversion_line'] = (high.rolling(window=self.conversion_line_period).max() + low.rolling(window=self.conversion_line_period).min()) / 2
        self.data['base_line'] = (high.rolling(window=self.base_line_period).max() + low.rolling(window=self.base_line_period).min()) / 2
        self.data['leading_span_a'] = ((self.data['conversion_line'] + self.data['base_line']) / 2).shift(self.base_line_period)
        self.data['leading_span_b'] = ((high.rolling(window=self.leading_span_b_period).max() + low.rolling(window=self.leading_span_b_period).min()) / 2).shift(self.base_line_period)
        self.data['lagging_span'] = close.shift(-self.lagging_span_period)

        # Define buy and sell signals
        # Buy signal: when Conversion Line crosses above Base Line and price is above Cloud
        self.data['signal'] = numpy.where(
            (self.data['conversion_line'] > self.data['base_line']) &
            (close > self.data['leading_span_a']) &
            (close > self.data['leading_span_b']), 1, 0)

        # Sell signal: when Conversion Line crosses below Base Line and price is below Cloud
        self.data['signal'] = numpy.where(
            (self.data['conversion_line'] < self.data['base_line']) &
            (close < self.data['leading_span_a']) &
            (close < self.data['leading_span_b']), -1, self.data['signal'])

        return self.data['signal']
    

class VWAP(Strategy):
    def __init__(self):
        # VWAP doesn't require any specific parameters for initialization but can be extended if needed
        pass

    def add_to_ax(self, ax):
        """
        Adds the VWAP plot to the provided Axes object.

        :param ax: The Axes object to plot on.
        """
        ax.plot(self.data.date, self.data['vwap'], color='purple', label='VWAP')
        ax.set_ylabel('VWAP Strategy')
        ax.legend()

    @Strategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        """
        Generates trading signals based on the Volume-Weighted Average Price (VWAP).

        :param dataframe: The input DataFrame containing 'close' and 'volume' columns.
        :return: A DataFrame with the 'vwap' and 'signal' columns added.
        """
        if not all(col in dataframe.columns for col in ['close', 'volume']):
            raise ValueError("Dataframe must contain 'close' and 'volume' columns")

        # Calculate VWAP
        cum_volume_price = (dataframe['close'] * dataframe['volume']).cumsum()
        cum_volume = dataframe['volume'].cumsum()
        self.data['vwap'] = cum_volume_price / cum_volume

        # Generate signals: 1 for buy, -1 for sell, based on price crossing above/below VWAP
        self.data['signal'] = 0  # Default to no signal
        self.data.loc[dataframe['close'] > self.data['vwap'], 'signal'] = 1  # Buy signal
        self.data.loc[dataframe['close'] < self.data['vwap'], 'signal'] = -1  # Sell signal

        return self.data['signal']


class MACD(Strategy):
    def __init__(
            self, 
            short_period: int = 12,
              long_period: int = 26, 
              signal_period: int = 9):
        """
        Initializes the MACD strategy.

        :param short_period: The number of periods for the short-term EMA.
        :param long_period: The number of periods for the long-term EMA.
        :param signal_period: The number of periods for the signal line EMA.
        """
        self.short_period = short_period
        self.long_period = long_period
        self.signal_period = signal_period

    def add_to_ax(self, ax):
        """
        Adds the MACD line, signal line, and histogram to the provided Axes object.

        :param ax: The Axes object to plot on.
        """
        ax.plot(self.data.date, self.data['macd_line'], label='MACD Line', color='blue')
        ax.plot(self.data.date, self.data['signal_line'], label='Signal Line', color='orange')
        ax.bar(self.data.date, self.data['histogram'], label='Histogram', color='green', width=0.7, align='center')
        ax.set_ylabel('MACD Strategy')
        ax.legend()

    @Strategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        """
        Generates trading signals based on the MACD strategy.

        :param dataframe: The input DataFrame containing 'close' column.
        :return: A DataFrame with the 'macd_line', 'signal_line', 'histogram', and 'signal' columns added.
        """
        if 'close' not in dataframe.columns:
            raise ValueError("Dataframe must contain 'close' column")

        # Calculate MACD Line as the difference between the short-period EMA and the long-period EMA
        ema_short = dataframe['close'].ewm(span=self.short_period, adjust=False).mean()
        ema_long = dataframe['close'].ewm(span=self.long_period, adjust=False).mean()
        self.data['macd_line'] = ema_short - ema_long

        # Calculate Signal Line as the EMA of the MACD Line
        self.data['signal_line'] = self.data['macd_line'].ewm(span=self.signal_period, adjust=False).mean()

        # Calculate Histogram as the difference between the MACD Line and the Signal Line
        self.data['histogram'] = self.data['macd_line'] - self.data['signal_line']

        # Generate signals: Buy (1) when MACD Line crosses above Signal Line, Sell (-1) when below
        self.data['signal'] = 0  # Default to no signal
        self.data.loc[self.data['macd_line'] > self.data['signal_line'], 'signal'] = 1  # Buy signal
        self.data.loc[self.data['macd_line'] < self.data['signal_line'], 'signal'] = -1  # Sell signal

        return self.data['signal']

class StochasticOscillator(Strategy):
    def __init__(
            self, 
            k_period: int = 14, 
            d_period: int = 3, 
            overbought_threshold: float = 80, 
            oversold_threshold: float = 20):
        """
        Initializes the Stochastic Oscillator strategy.

        :param k_period: The number of periods for the %K line calculation.
        :param d_period: The number of periods for the %D line calculation.
        :param overbought_threshold: The threshold above which the market is considered overbought.
        :param oversold_threshold: The threshold below which the market is considered oversold.
        """
        self.k_period = k_period
        self.d_period = d_period
        self.overbought_threshold = overbought_threshold
        self.oversold_threshold = oversold_threshold

    def add_to_ax(self, ax):
        """
        Adds the %K and %D lines of the Stochastic Oscillator to the provided Axes object, along with overbought and oversold threshold lines.

        :param ax: The Axes object to plot on.
        """
        ax.plot(self.data.date, self.data['%k_line'], label='%K Line', color='blue')
        ax.plot(self.data.date, self.data['%d_line'], label='%D Line', color='orange')
        ax.axhline(self.overbought_threshold, linestyle='--', color='red', label='Overbought')
        ax.axhline(self.oversold_threshold, linestyle='--', color='green', label='Oversold')
        ax.set_ylabel('Stochastic Oscillator Strategy')
        ax.legend()

    @Strategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        """
        Generates trading signals based on the Stochastic Oscillator strategy.

        :param dataframe: The input DataFrame containing 'high', 'low', and 'close' columns.
        :return: A DataFrame with the '%k_line', '%d_line', and 'signal' columns added.
        """
        if not all(col in dataframe.columns for col in ['high', 'low', 'close']):
            raise ValueError("Dataframe must contain 'high', 'low', and 'close' columns")

        # Calculate %K Line
        low_min = dataframe['low'].rolling(window=self.k_period).min()
        high_max = dataframe['high'].rolling(window=self.k_period).max()
        self.data['%k_line'] = ((dataframe['close'] - low_min) / (high_max - low_min)) * 100

        # Calculate %D Line as the moving average of %K Line
        self.data['%d_line'] = self.data['%k_line'].rolling(window=self.d_period).mean()

        # Generate signals
        self.data['signal'] = 0  # Default to no signal
        # Buy signal: %K crosses above %D from below the oversold threshold
        buy_signal = ((self.data['%k_line'] > self.data['%d_line']) & 
                      (self.data['%k_line'].shift(1) <= self.data['%d_line'].shift(1)) & 
                      (self.data['%k_line'] < self.oversold_threshold))
        # Sell signal: %K crosses below %D from above the overbought threshold
        sell_signal = ((self.data['%k_line'] < self.data['%d_line']) & 
                       (self.data['%k_line'].shift(1) >= self.data['%d_line'].shift(1)) & 
                       (self.data['%k_line'] > self.overbought_threshold))

        self.data.loc[buy_signal, 'signal'] = 1
        self.data.loc[sell_signal, 'signal'] = -1

        return self.data['signal']

class ROC(Strategy):
    def __init__(
            self, 
            roc_period: int = 14):
        """
        Initializes the Price Rate of Change strategy.

        :param roc_period: The number of periods over which the ROC is calculated.
        """
        self.roc_period = roc_period

    def add_to_ax(self, ax):
        """
        Adds the ROC plot to the provided Axes object.

        :param ax: The Axes object to plot on.
        """
        ax.plot(self.data.date, self.data['roc'], label='ROC', color='blue')
        ax.axhline(0, linestyle='--', color='red', label='Zero Line')
        ax.set_ylabel('Price Rate of Change Strategy')
        ax.legend()

    @Strategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        """
        Generates trading signals based on the Price Rate of Change strategy.

        :param dataframe: The input DataFrame containing at least a 'close' column.
        :return: A DataFrame with the 'roc' and 'signal' columns added.
        """
        if 'close' not in dataframe.columns:
            raise ValueError("Dataframe must contain 'close' column")

        # Calculate ROC
        self.data['roc'] = ((dataframe['close'] - dataframe['close'].shift(self.roc_period)) / dataframe['close'].shift(self.roc_period)) * 100

        # Generate signals: Buy (1) when ROC crosses above zero, Sell (-1) when ROC crosses below zero
        self.data['signal'] = 0  # Default to no signal
        self.data.loc[self.data['roc'] > 0, 'signal'] = 1  # Buy signal
        self.data.loc[self.data['roc'] < 0, 'signal'] = -1  # Sell signal

        return self.data['signal']
    

class ParabolicSAR(Strategy):
    def __init__(
            self, 
            start_af: float = 0.02, 
            increment_af: float = 0.02, 
            max_af: float = 0.2):
        """
        Initializes the Parabolic SAR strategy.

        :param start_af: The starting acceleration factor.
        :param increment_af: The increment to the acceleration factor for each new extreme point.
        :param max_af: The maximum acceleration factor.
        """
        self.start_af = start_af
        self.increment_af = increment_af
        self.max_af = max_af

    def add_to_ax(self, ax):
        """
        Adds the Parabolic SAR plot to the provided Axes object.

        :param ax: The Axes object to plot on.
        """
        ax.plot(self.data.date, self.data['sar'], label='Parabolic SAR', color='red', marker='o', markersize=4)
        ax.set_ylabel('Parabolic SAR Strategy')
        ax.legend()

    @Strategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        """
        Generates trading signals based on the Parabolic SAR strategy.

        :param dataframe: The input DataFrame containing at least 'high', 'low', and 'close' columns.
        :return: A DataFrame with the 'sar' and 'signal' columns added.
        """
        if not all(col in dataframe.columns for col in ['high', 'low', 'close']):
            raise ValueError("Dataframe must contain 'high', 'low', and 'close' columns")

        # Initialize Parabolic SAR calculation variables
        sar = dataframe['high'].copy()
        ep = dataframe['high'].iloc[0]  # Extreme Point
        af = self.start_af  # Acceleration Factor
        uptrend = True

        for i in range(1, len(dataframe)):
            prev_sar = sar.iloc[i - 1]
            if uptrend:
                sar.iloc[i] = prev_sar + af * (ep - prev_sar)
                if dataframe['low'].iloc[i] < sar.iloc[i]:
                    uptrend = False
                    sar.iloc[i] = ep
                    ep = dataframe['low'].iloc[i]
                    af = self.start_af
                else:
                    if dataframe['high'].iloc[i] > ep:
                        ep = dataframe['high'].iloc[i]
                        af = min(af + self.increment_af, self.max_af)
                    sar.iloc[i] = min(sar.iloc[i], dataframe['low'].iloc[i], dataframe['low'].iloc[i-1])
            else:
                sar.iloc[i] = prev_sar - af * (prev_sar - ep)
                if dataframe['high'].iloc[i] > sar.iloc[i]:
                    uptrend = True
                    sar.iloc[i] = ep
                    ep = dataframe['high'].iloc[i]
                    af = self.start_af
                else:
                    if dataframe['low'].iloc[i] < ep:
                        ep = dataframe['low'].iloc[i]
                        af = min(af + self.increment_af, self.max_af)
                    sar.iloc[i] = max(sar.iloc[i], dataframe['high'].iloc[i], dataframe['high'].iloc[i-1])

        self.data['sar'] = sar

        # Generate signals: Buy (1) when price crosses above SAR, Sell (-1) when price crosses below SAR
        self.data['signal'] = 0  # Default to no signal
        self.data.loc[dataframe['close'] > self.data['sar'], 'signal'] = 1  # Buy signal
        self.data.loc[dataframe['close'] < self.data['sar'], 'signal'] = -1  # Sell signal

        return self.data['signal']

# -
