from TradeTide import BackTester, indicators, get_market_data, Strategy
from TradeTide import capital_managment, loss_profit_managment

market_data = get_market_data('eur', 'usd', year=2023, time_span='3 days')

indicator_0 = indicators.StochRSIIndicator()
indicator_1 = indicators.RelativeStrengthIndex()

strategy = Strategy(indicator_0, indicator_1)

backtester = BackTester(market=market_data, strategy=strategy)

loss_profit_managment = loss_profit_managment.DirectLossProfitManagement(
    stop_loss='.1%',
    take_profit='.1%',
)

capital_managment = capital_managment.LimitedCapital(
    initial_capital=1_000,
    spread=0,
    loss_profit_managment=loss_profit_managment,
    max_cap_per_trade=100,
    limit_of_positions=1
)

backtester.backtest(capital_managment=capital_managment)

backtester.plot(show_assets=True, show_price=True)

backtester.calculate_performance_metrics()

final_portfolio_value = backtester.get_final_portfolio_value()

# -
