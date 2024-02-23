from TradeTide import BackTester, RelativeStrengthIndex, get_market_data

market_data = get_market_data('eur', 'usd', year=2023)

strategy = RelativeStrengthIndex(period='30min', overbought_threshold=90, oversold_threshold=10)

strategy.generate_signal(market_data)

backtester = BackTester(market=market_data, strategy=strategy)

backtester.back_test(stop_loss='.1%', take_profit='.1%', spread=0)

portfolio = backtester.portfolio

backtester.plot()

backtester.calculate_performance_metrics()

final_portfolio_value = backtester.get_final_portfolio_value()

print(f"Final Portfolio Value: {final_portfolio_value}")