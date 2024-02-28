from TradeTide import BackTester, indicators, get_market_data
from TradeTide.capital_managment import LimitedCapital

market_data = get_market_data('eur', 'usd', year=2023, time_span='1 days')


strategy = indicators.StochRSIIndicator()

strategy.generate_signal(market_data)

backtester = BackTester(market=market_data, strategy=strategy)

capital_managment = LimitedCapital(
    initial_capital=1_000,
    spread=0,
    stop_loss='.1%',
    take_profit='.1%',
    max_cap_per_trade=100,
    limit_of_positions=3
)

backtester.backtest(capital_managment=capital_managment)

portfolio = backtester.portfolio

backtester.plot(show_assets=True, show_price=True)

backtester.calculate_performance_metrics()

final_portfolio_value = backtester.get_final_portfolio_value()

# -
