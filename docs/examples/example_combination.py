# Import necessary modules and classes from the TradeTide package
from TradeTide import BackTester, indicators, get_market_data, Strategy
from TradeTide.capital_managment import LimitedCapital
from TradeTide.risk_management import DirectLossProfitManagement

# Load historical market data for EUR/USD pair for the year 2023 and limit to 4000 data points
market_data = get_market_data('eur', 'usd', year=2023, time_span='30day', spread=0)

# Initialize a Moving Average Crossing indicator with specific window settings and minimum period
indicator_0 = indicators.BollingerBands()
indicator_1 = indicators.RelativeMomentumIndex()

strategy = Strategy(
    indicator_0, indicator_1
)

# Generate trading signals based on the market data
strategy.generate_signal(market_data)

# Plot the indicator signals overlaid on the market data
strategy.plot()

# Create the BackTester instance, linking it with the market data and chosen strategy
backtester = BackTester(market=market_data, strategy=strategy)

# Set up loss and profit management with specified stop loss and take profit percentages
loss_profit_managment = DirectLossProfitManagement(
    stop_loss='.1%',  # Stop loss percentage
    take_profit='.1%',  # Take profit percentage
)

# Configure capital management strategy with initial capital, spread, and trading constraints
capital_managment = LimitedCapital(
    initial_capital=1_000,  # Starting capital
    risk_management=loss_profit_managment,  # Loss and profit management strategy
    max_cap_per_trade=100,  # Maximum capital allocated per trade
    limit_of_positions=3  # Maximum number of concurrent open positions
)

# Execute the backtest using the configured capital management strategy
backtester.backtest(capital_managment=capital_managment)

# Retrieve and display the last few rows of the resulting portfolio DataFrame
portfolio = backtester.portfolio
print(portfolio.tail())

# Visualize the backtest results, showing the strategy's performance against the market price
backtester.plot(show_price=True)

# Calculate and display key performance metrics for the trading strategy
backtester.calculate_performance_metrics()

# Retrieve and print the final total value of the portfolio after completing the backtest
backtester.print_metrics()


# -
