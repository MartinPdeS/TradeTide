#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from typing import NoReturn
import pandas
import numpy
from TradeTide.strategy import Strategy
from TradeTide.plottings import PlotTrade
from TradeTide.tools import percent_to_float
from TradeTide.position import Position


class BackTester():
    """
    A class for backtesting forex trading strategies.

    The ForexBacktester takes a trading strategy, applies it to historical forex data, and simulates the execution
    of trades based on the signals generated by the strategy. It tracks the performance of these trades over time,
    allowing for the evaluation of the strategy's effectiveness.
    """

    def __init__(self, market: pandas.DataFrame, strategy: Strategy):
        """
        Initializes a new instance of the BackTester class with specified market data and trading strategy.

        The BackTester class is designed to simulate trading activity using historical market data and a predefined trading
        strategy. It sets up the environment for backtesting by associating the given market data and strategy with the instance,
        preparing it to execute the backtest through subsequent methods.

        Parameters:
            market (pandas.DataFrame): The historical market data to be used for backtesting. This DataFrame should include
                                       columns relevant to the trading strategy, such as 'date', 'open', 'high', 'low', 'close',
                                       and optionally 'volume', among others.
            strategy (Strategy): An instance of a trading strategy derived from the Strategy class. This strategy should
                                     implement methods for generating trading signals based on the provided market data.

        Attributes:
            market_dataframe (pandas.DataFrame): Stores the provided market data for use in backtesting.
            strategy (Strategy): The trading strategy to be backtested.
            portfolio (pandas.DataFrame or None): Initialized as None, this attribute is intended to store the results of the
                                                   backtest, including the performance of the trading strategy over time. It will
                                                   be populated and updated during the backtesting process.

        Note:
            The 'market_dataframe' must be pre-processed if necessary before passing to this initializer to ensure compatibility
            with the 'strategy'. The 'strategy' instance must be properly configured with any required parameters prior to
            initialization of the BackTester.
        """
        self.market = market
        self.strategy = strategy
        self.portfolio = None

    def signals_to_positions(self) -> NoReturn:
        """
        Transforms trading signals into positions by interpreting changes in the signals.

        This method updates positions based on the following rules:
        - A positive change in the signal (e.g., from 0 to 1) indicates entering a long position.
        - A negative change in the signal (e.g., from 1 to 0 or 1 to -1) indicates exiting a long position or entering a short position.
        - Continuous signals (no change) imply holding the current position.
        - Direct reversals (e.g., from -1 to 1) are allowed and indicate switching positions.

        The 'positions' column in the portfolio DataFrame is updated to reflect the current trading position.
        """
        # Calculate the difference to detect changes in the signal
        signal_changes = self.strategy.signal.diff()

        # Determine positions: 1 for long, -1 for short, 0 for no position
        self.portfolio['positions'] = numpy.select(
            [
                signal_changes > 0,  # Condition for entering a long position
                signal_changes < 0,  # Condition for entering a short position or exiting
            ],
            [
                1,  # Value for entering a long position
                numpy.where(self.strategy.signal == -1, -1, 0)  # Enter short position if signal is -1, else exit
            ],
            default=self.strategy.signal  # Default to the current signal, allowing for direct reversals and continuous holding
        )

        # Forward fill to maintain positions until the next change
        self.portfolio['positions'].ffill(inplace=True)

        # Fill initial NaN values with 0 (no position at start)
        self.portfolio['positions'].fillna(0, inplace=True)

    def backtest(
            self,
            stop_loss: float | str = '0.1%',
            take_profit: float | str = '0.1%',
            initial_capital: float = 100_000,
            spread: float = 0.1,
            return_extra_data: bool = False,
            max_cap_per_trade: float = 1_000) -> pandas.DataFrame:
        """
        Executes a backtest of the trading strategy using historical market data, with customizable trading parameters.

        The backtest simulates trading activity based on signals generated by the strategy, adjusting for specified stop loss, take profit,
        and other trading parameters. It calculates the resulting portfolio value over time, taking into account transaction costs and
        capital limitations per trade.

        Parameters:
            stop_loss (float | str, optional): The stop loss threshold, specified as a percentage (e.g., '1%') or a float. Default is '0.1%'.
            take_profit (float | str, optional): The take profit threshold, specified as a percentage (e.g., '1%') or a float. Default is '0.1%'.
            initial_capital (float, optional): The initial capital available for trading. Default is 100,000.
            spread (float, optional): The spread between buy and sell prices as a percentage of the price. Default is 0.01 (1%).
            return_extra_data (bool, optional): If True, the method returns additional data related to the backtest. Default is False.
            max_cap_per_trade (float, optional): The maximum capital allocated per trade. Default is 1,000.

        Returns:
            pandas.DataFrame: A DataFrame representing the portfolio's performance over time. If `return_extra_data` is True, it also
                              returns a DataFrame containing additional backtest-related data.

        The portfolio DataFrame contains columns for dates, trading signals, position changes, and other metrics relevant to evaluating
        the strategy's performance. If `return_extra_data` is True, the additional DataFrame includes detailed information about each trade
        and market conditions at the time of trading.
        """
        stop_loss = percent_to_float(stop_loss)
        take_profit = percent_to_float(take_profit)

        self.initial_capital = initial_capital

        self.manage_positions(
            market=self.market,
            spread=spread,
            stop_loss=stop_loss,
            take_profit=take_profit,
            max_cap_per_trade=max_cap_per_trade
        )

        self.generate_portfolio()

        return self.portfolio

    def generate_portfolio(self) -> NoReturn:
        self.portfolio = pandas.DataFrame(
            0.0,
            index=self.market.index,
            columns=['units', 'holdings', 'short_positions', 'long_positions', 'cash'])

        self.portfolio['cash'] = float(self.initial_capital)

        # Calculate cumulative holdings and cash, considering the units bought and the entry price
        for position in self.position_list:
            position.update_portfolio_dataframe(dataframe=self.portfolio)

        # # Total portfolio value and percentage returns
        self.portfolio['total'] = self.portfolio['cash'] + self.portfolio['holdings']
        self.portfolio['returns'] = self.portfolio['total'].ffill().pct_change()

    def manage_positions(
            self,
            market: pandas.DataFrame,
            spread: float,
            stop_loss: float,
            take_profit: float,
            max_cap_per_trade: float) -> NoReturn:
        """
        Optimizes the management of trading positions, leveraging Pandas for pre-processing and NumPy for efficient storage.
        This method identifies new trading signals, calculates entry prices and units, instantiates Position objects for each
        trade, and stores these objects in a NumPy array.

        The method enhances performance by minimizing loop iterations and utilizing vectorized operations for bulk data processing,
        making it significantly faster for managing large datasets or frequent trading signals.

        Parameters:
            market (pandas.DataFrame): The DataFrame containing historical market data. It must include a 'close' column
                                       with the closing prices of the asset being traded.
            spread (float): The transaction cost represented as a spread applied to the entry price of each new position.
                            This cost is subtracted from the entry price for buys and added for sells.
            stop_loss (float): The stop-loss threshold, expressed as a decimal. It represents the maximum loss a trader is
                               willing to accept. A position is closed if the price falls below this threshold for long positions
                               or rises above it for short positions.
            take_profit (float): The take-profit threshold, also expressed as a decimal. It represents the price level at which
                                 a position is closed to realize gains.
            max_cap_per_trade (float): The maximum capital allocated for each trade. This value is used to calculate the number
                                       of units to be traded based on the entry price and spread.

        Updates:
            self.positions_array (np.array): A NumPy array that stores references to Position instances created for each new
                                             trading signal identified. This array replaces the previous list-based storage
                                             to enhance access performance and memory efficiency.

        Note:
            This method assumes that there is an existing 'strategy' attribute in the calling object which provides trading signals
            through a 'signal' DataFrame column. Signals are interpreted as follows: a positive value indicates a 'buy' signal,
            a negative value indicates a 'sell' signal, and a zero value indicates no action.
            The portfolio management, including the calculation of stop-loss and take-profit levels and the decision to open or close
            positions, is based solely on these signals and the parameters provided to this method.

        """
        # Detect new positions based on strategy signals
        signals = self.strategy.signal
        new_positions_idx = signals[signals.diff().fillna(0) != 0].index

        # Initialize or clear the list to store Position objects
        self.position_list = []

        # Iterate over signals and open new positions where indicated
        for date in new_positions_idx:
            if self.strategy.signal.loc[date] != 0:  # Ensure there's an actionable signal

                entry_price: float = self.market.loc[date, 'close'] + spread
                units: int = numpy.floor((max_cap_per_trade - spread) / entry_price)
                position_type: str = 'long' if self.strategy.signal.loc[date] > 0 else 'short'

                position = Position(
                    start_date=date,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    market=market,
                    units=units,
                    entry_price=entry_price,
                    position_type=position_type
                )

                self.position_list.append(position)

    def plot(self, **kwargs) -> NoReturn:
        """
        Generates a visual representation of the backtest results using the PlotTrade class.

        This method constructs a figure that includes plots for market data, trading signals, and portfolio metrics,
        providing a comprehensive overview of the trading strategy's performance over the backtesting period.

        The figure is constructed and displayed immediately, utilizing the market data, portfolio results, and the
        strategy instance associated with this BackTester.

        Note:
            The method assumes that the backtest has been run and the `portfolio` attribute of the BackTester class
            has been populated with trading data and results.
        """
        plot = PlotTrade(
            backtester=self,
            market=self.market,
            portfolio=self.portfolio,
            strategy=self.strategy,
        )

        plot.plot_trading_strategy(**kwargs)

    def get_final_portfolio_value(self) -> float:
        """
        Retrieves the final total value of the portfolio at the end of the backtesting period.

        This method calculates the final value of the portfolio, considering all open and closed positions, and prints
        this value to the console. It is a useful metric for assessing the absolute performance of the trading strategy.

        Returns:
            float: The final total value of the portfolio, represented as a monetary amount.

        Note:
            This method should be called after completing the backtest to ensure the portfolio contains the final trading results.
        """
        final_portfolio_value = self.portfolio['total'].iloc[-1]

        print(f"Final Portfolio Value: ${final_portfolio_value:.2f}")

        return final_portfolio_value

    def calculate_performance_metrics(self) -> NoReturn:
        """
        Calculates and displays key performance metrics for the trading strategy based on the backtest results.

        This method computes several important metrics, including total return, annualized return, maximum drawdown,
        Sharpe ratio, and the win-loss ratio. These metrics provide a quantitative evaluation of the strategy's effectiveness
        and risk characteristics over the backtesting period.

        The calculated metrics are printed to the console for review and analysis.

        Preconditions:
            - The backtest must have been executed, and the `portfolio` attribute should contain the trading results.
            - The `initial_capital` attribute must be set to the initial capital used in the backtest.

        Note:
            If the portfolio is not yet populated (i.e., the backtest has not been run), the method will print a message
            indicating that the backtest should be executed first.
        """
        if self.portfolio is None:
            print("Backtest the strategy first before calculating performance metrics.")
            return

        # Total Return
        total_return = (self.portfolio['total'].iloc[-1] / self.initial_capital) - 1

        # Annualized Return
        trading_days = self.market.time_span.days
        annualized_return = ((1 + total_return) ** (365.0 / trading_days)) - 1

        # Maximum Drawdown
        rolling_max = self.portfolio['total'].cummax()
        drawdown = self.portfolio['total'] / rolling_max - 1.0
        max_drawdown = drawdown.min()

        # Sharpe Ratio (Assuming risk-free rate is 0 for simplicity)
        daily_returns = self.portfolio['returns']
        sharpe_ratio = daily_returns.mean() / daily_returns.std() * numpy.sqrt(252)

        # Win-Loss Ratio
        wins = len(self.portfolio[self.portfolio['returns'] > 0])
        losses = len(self.portfolio[self.portfolio['returns'] < 0])
        win_loss_ratio = wins / losses if losses != 0 else numpy.inf

        # Print the metrics
        print(f"Total Return: {total_return * 100:.2f}%")
        print(f"Annualized Return: {annualized_return * 100:.2f}%")
        print(f"Maximum Drawdown: {max_drawdown * 100:.2f}%")
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"Win-Loss Ratio: {win_loss_ratio:.2f}")

# -
