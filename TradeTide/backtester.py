from typing import NoReturn
import pandas
import numpy
from TradeTide.strategy import BaseStrategy
from TradeTide.plottings import PlotTrade
from TradeTide.tools import percent_to_float


class BackTester():
    """
    A class for backtesting forex trading strategies.

    The ForexBacktester takes a trading strategy, applies it to historical forex data, and simulates the execution
    of trades based on the signals generated by the strategy. It tracks the performance of these trades over time,
    allowing for the evaluation of the strategy's effectiveness.
    """

    def __init__(self, market: pandas.DataFrame, strategy: BaseStrategy):
        """
        Initializes a new instance of the BackTester class with specified market data and trading strategy.

        The BackTester class is designed to simulate trading activity using historical market data and a predefined trading
        strategy. It sets up the environment for backtesting by associating the given market data and strategy with the instance,
        preparing it to execute the backtest through subsequent methods.

        Parameters:
            market (pandas.DataFrame): The historical market data to be used for backtesting. This DataFrame should include
                                       columns relevant to the trading strategy, such as 'date', 'open', 'high', 'low', 'close',
                                       and optionally 'volume', among others.
            strategy (BaseStrategy): An instance of a trading strategy derived from the BaseStrategy class. This strategy should
                                     implement methods for generating trading signals based on the provided market data.

        Attributes:
            market_dataframe (pandas.DataFrame): Stores the provided market data for use in backtesting.
            strategy (BaseStrategy): The trading strategy to be backtested.
            portfolio (pandas.DataFrame or None): Initialized as None, this attribute is intended to store the results of the
                                                   backtest, including the performance of the trading strategy over time. It will
                                                   be populated and updated during the backtesting process.

        Note:
            The 'market_dataframe' must be pre-processed if necessary before passing to this initializer to ensure compatibility
            with the 'strategy'. The 'strategy' instance must be properly configured with any required parameters prior to
            initialization of the BackTester.
        """
        self.market_dataframe = market
        self.strategy = strategy
        self.portfolio = None

    def manage_positions(self, market: pandas.DataFrame, spread: float, stop_loss: float, take_profit: float) -> NoReturn:
        """
        Manages the opening and closing of trading positions based on stop loss and take profit thresholds, adjusted for spread.

        This method updates the portfolio DataFrame to include entry prices for new positions (adjusted for spread), and calculates
        stop loss and take profit price levels for each open position. It then checks market data to determine if these levels are
        breached, indicating whether a position should be closed due to stop loss or take profit conditions being met.

        Parameters:
            market (pandas.DataFrame): The DataFrame containing historical market data with 'close', 'low', and 'high' price columns.
            spread (float): The spread applied to the entry price of a new position, representing the transaction cost.
            stop_loss (float): The stop loss threshold, expressed as a decimal (e.g., 0.1 for 10%). Positions are closed if the market
                               price drops below this threshold relative to the entry price.
            take_profit (float): The take profit threshold, expressed as a decimal (e.g., 0.1 for 10%). Positions are closed if the market
                                 price rises above this threshold relative to the entry price.

        Updates:
            The portfolio DataFrame is updated in-place to include the following columns:
            - 'opened_positions': Tracks newly opened positions.
            - 'entry_price': The entry price for each position, adjusted for the spread.
            - 'stop_loss_price': The price level at which a stop loss would be triggered.
            - 'take_profit_price': The price level at which a take profit would be triggered.
            - 'stop_loss_triggered': A boolean flag indicating if the stop loss condition has been met.
            - 'take_profit_triggered': A boolean flag indicating if the take profit condition has been met.
            - 'close_positions': A boolean flag indicating if a position should be closed due to stop loss or take profit conditions.

        Note:
            This method assumes the 'positions' column in the portfolio DataFrame tracks the current open positions, where a value of
            1 indicates a new buy position. The method modifies the portfolio DataFrame in-place and does not return a value.
        """

        # Aliasing portfolio
        portfolio = self.portfolio

        # Initialize 'opened_positions' to track the status of new trades
        portfolio['opened_positions'] = portfolio['positions']

        # Entry price includes the spread for buy positions
        portfolio['entry_price'] = market['close'].where(portfolio['positions'] == 1) + spread  # maybe + spread

        # Forward fill entry prices for the holding period
        portfolio['entry_price'] = portfolio['entry_price'].ffill()

        # Calculate stop-loss and take-profit prices
        portfolio['stop_loss_price'] = portfolio['entry_price'] * (1 - stop_loss)
        portfolio['take_profit_price'] = portfolio['entry_price'] * (1 + take_profit)

        # Check if stop-loss or take-profit were triggered
        portfolio['stop_loss_triggered'] = market['low'] < portfolio['stop_loss_price']
        portfolio['take_profit_triggered'] = market['high'] > portfolio['take_profit_price']

        # Close positions where stop-loss or take-profit conditions are met
        portfolio['close_positions'] = portfolio['stop_loss_triggered'] | portfolio['take_profit_triggered']
        portfolio.loc[portfolio['close_positions'], 'positions'] = 0

    def calculate_units_and_portfolio(
            self,
            market: pandas.DataFrame,
            initial_capital: float,
            spread: float,
            max_cap_per_trade: float):
        """
        Calculates the number of units to buy for each trade based on available capital, spread, and market conditions,
        and updates the portfolio DataFrame with these calculations.

        This method computes the feasible number of units for each trade while adhering to the constraints of initial capital,
        maximum capital allocation per trade, and the transaction spread. It updates the portfolio with details of holdings,
        cash balance, total value, and returns over time.

        Parameters:
            market (pandas.DataFrame): The DataFrame containing historical market data, including at least 'close' prices and dates.
            initial_capital (float): The initial capital available for trading.
            spread (float): The transaction spread, representing the cost of trading, deducted from the capital allocated per trade.
            max_cap_per_trade (float): The maximum amount of capital allocated for each trade.

        The method updates the portfolio DataFrame in-place, adding columns for:
            - 'units': The number of units bought in each trade.
            - 'holdings': The cumulative value of the holdings over time.
            - 'cash': The cash balance after each trade, considering the cost of purchased units and the spread.
            - 'total': The total value of the portfolio (cash + holdings) over time.
            - 'returns': The percentage return of the portfolio, calculated from the total value.

        Note:
            - The method assumes that 'entry_price' is a column in the portfolio DataFrame, representing the price at which each trade is entered.
            - The 'market' DataFrame must include a 'close' column, which represents the closing price of the asset.
            - The method modifies the portfolio DataFrame in-place; it does not return a new DataFrame.
        """
        # Aliasing portfolio
        portfolio = self.portfolio

        # Determine the number of units that can be bought with the available capital per trade
        portfolio['units'] = numpy.floor((max_cap_per_trade - spread) / portfolio['entry_price'])

        # Calculate cumulative holdings and cash, considering the units bought and the entry price
        portfolio['holdings'] = (portfolio['units'] * market['close']).cumsum()
        portfolio['cash'] = initial_capital - (portfolio['units'] * portfolio['entry_price']).cumsum()

        # Total portfolio value and percentage returns
        portfolio['total'] = portfolio['cash'] + portfolio['holdings']
        portfolio['returns'] = portfolio['total'].ffill().pct_change()

    def back_test(
            self,
            stop_loss: float | str = '0.1%',
            take_profit: float | str = '0.1%',
            buy_unit: float = 1_000,
            initial_capital: float = 100_000,
            spread: float = 0.01,
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
            buy_unit (float, optional): The number of units to buy per trade. Default is 1,000.
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
        market = self.market_dataframe.copy()

        # Initialize the portfolio DataFrame
        portfolio = self.portfolio = pandas.DataFrame(index=market.index)
        portfolio['date'] = market['date']

        portfolio['signal'] = self.strategy.signal

        portfolio['positions'] = portfolio['signal'].diff()

        portfolio.at[portfolio.index[0], 'positions'] = 0

        self.manage_positions(
            market=market,
            spread=spread,
            stop_loss=stop_loss,
            take_profit=take_profit
        )

        self.calculate_units_and_portfolio(
            market=market,
            initial_capital=initial_capital,
            spread=spread,
            max_cap_per_trade=max_cap_per_trade
        )

        self.data = market

        if return_extra_data:
            return self.portfolio, market

        return self.portfolio

    def plot(self) -> NoReturn:
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
            market=self.market_dataframe,
            portfolio=self.portfolio,
            strategy=self.strategy,
        )

        plot.construct_figure()

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
        trading_days = len(self.portfolio)
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
