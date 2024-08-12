from TradeTide import BackTester, indicators, get_market_data, Strategy
from TradeTide import capital_management, risk_management

market_data = get_market_data('eur', 'usd', year=2023, time_span='10 days', spread=10)

indicator_0 = indicators.MAC()
indicator_1 = indicators.RSI()

strategy = Strategy(indicator_0)

strategy.generate_signal(market_data)

backtester = BackTester(market=market_data, strategy=strategy)

risk = risk_management.DirectLossProfit(
    market=market_data,
    stop_loss='20pip',
    take_profit='10pip',
)

cap_managment = capital_management.LimitedCapital(
    initial_capital=100_000,
    risk_management=risk,
    # add leverage
    max_cap_per_trade=10_000,
    limit_of_positions=1,
    micro_lot=1_000,
    max_spread=1,
)

backtester.backtest(capital_management=cap_managment)

backtester.plot(
    show_price=True,
    show_total=True,
    show_assets=True,
    # show_units=True,
    # show_positions=True
)

# backtester.calculate_performance_metrics()

backtester.metrics.print()

# -
