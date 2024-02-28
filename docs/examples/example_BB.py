from TradeTide import BackTester, indicators, get_market_data
from TradeTide.capital_managment import LimitedCapital

# Load historical market data
market_data = get_market_data('eur', 'usd', year=2023)

market_data = market_data[:4_000]

# Initialize the trading strategy
strategy = indicators.BollingerBands()

strategy.generate_signal(market_data)

# Create the BackTester instance with market data and strategy
backtester = BackTester(market=market_data, strategy=strategy)

capital_managment = LimitedCapital(
    initial_capital=1_000,
    spread=0,
    stop_loss='.1%',
    take_profit='.1%',
    max_cap_per_trade=100,
    limit_of_positions=3
)

# Run the backtest with the specified parameters
backtester.backtest(capital_managment=capital_managment)

# Access the resulting portfolio DataFrame
portfolio = backtester.portfolio
print(portfolio.tail())

# Plot the backtest results to visualize the strategy's performance
backtester.plot(show_price=True)

# Calculate and display key performance metrics of the trading strategy
backtester.calculate_performance_metrics()

# Retrieve the final total value of the portfolio after backtesting
final_portfolio_value = backtester.get_final_portfolio_value()
print(f"Final Portfolio Value: {final_portfolio_value}")

# -
