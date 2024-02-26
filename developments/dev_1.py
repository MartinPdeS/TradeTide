from TradeTide import BackTester, indicators, get_market_data

market_data = get_market_data('eur', 'usd', year=2023)

market_data = market_data[:600]

strategy = indicators.RelativeStrengthIndex(period='30min', overbought_threshold=70, oversold_threshold=30)

strategy.generate_signal(market_data)

backtester = BackTester(market=market_data, strategy=strategy)

backtester.back_test(stop_loss='.1%', take_profit='.1%', spread=0)

portfolio = backtester.portfolio

backtester.plot(
    show_price=True,
    show_metric=True,
    show_assets=True,
    show_positions=True,
    # show_units=True
)

# backtester.calculate_performance_metrics()

# final_portfolio_value = backtester.get_final_portfolio_value()

# print(f"Final Portfolio Value: {final_portfolio_value}")

# -
