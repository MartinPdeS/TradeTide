from TradeTide import BackTester, BollingerBands, get_market_data

# Load historical market data
market_data = get_market_data('eur', 'usd', year=2023)

market_data = market_data[:40_000]

# Initialize the trading strategy
strategy = BollingerBands()

strategy.generate_signal(market_data)

# Create the BackTester instance with market data and strategy
backtester = BackTester(market=market_data, strategy=strategy)

# Run the backtest with the specified parameters
backtester.back_test(stop_loss='.001', take_profit='.1%', spread=0)

# Access the resulting portfolio DataFrame
portfolio = backtester.portfolio
print(portfolio.tail())

# Plot the backtest results to visualize the strategy's performance
backtester.plot()

# Calculate and display key performance metrics of the trading strategy
backtester.calculate_performance_metrics()

# Retrieve the final total value of the portfolio after backtesting
final_portfolio_value = backtester.get_final_portfolio_value()
print(f"Final Portfolio Value: {final_portfolio_value}")

# -
