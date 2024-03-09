from TradeTide import BackTester, indicators, get_market_data, Strategy
from TradeTide import capital_managment, risk_management

market_data = get_market_data('eur', 'usd', year=2023, time_span='10 days', spread=0)

indicator_0 = indicators.MAC()
indicator_1 = indicators.RSI()

strategy = Strategy(indicator_0)

strategy.generate_signal(market_data)

backtester = BackTester(market=market_data, strategy=strategy)

risk = risk_management.DirectLossProfit(
    market=market_data,
    stop_loss='20pip',
    take_profit='20pip',
)

capital_managment = capital_managment.LimitedCapital(
    initial_capital=1_000,
    risk_management=risk,
    # add leverage
    max_cap_per_trade=100,
    limit_of_positions=1
)

backtester.backtest(capital_managment=capital_managment)

# backtester.plot(
#     show_price=True,
#     show_total=True,
#     show_assets=True,
#     show_units=True,
#     show_positions=True
# )

backtester.calculate_performance_metrics()

backtester.print_metrics()


ls = backtester.position_list[0]


ls.plot()


# final_portfolio_value = backtester.get_final_portfolio_value()

# -
