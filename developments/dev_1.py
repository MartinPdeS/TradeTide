from TradeTide import BackTester, indicators, get_market_data, Strategy
from TradeTide import capital_managment, risk_management

market_data = get_market_data('eur', 'usd', year=2023, time_span='9 days', spread=0)

indicator_0 = indicators.StochRSIIndicator()
indicator_1 = indicators.RelativeStrengthIndex()

strategy = Strategy(indicator_0, indicator_1)

backtester = BackTester(market=market_data, strategy=strategy)

loss_profit_managment = risk_management.DirectLossProfitManagement(
    stop_loss='.1%',
    take_profit='.1%',
)

capital_managment = capital_managment.LimitedCapital(
    initial_capital=1_000,
    risk_management=loss_profit_managment,
    max_cap_per_trade=100,
    limit_of_positions=3
)

backtester.backtest(capital_managment=capital_managment)

# backtester.plot(show_price=True)

backtester.calculate_performance_metrics()

backtester.print()

# final_portfolio_value = backtester.get_final_portfolio_value()

# -
