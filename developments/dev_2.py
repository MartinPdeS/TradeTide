from TradeTide import indicators, get_market_data, Strategy

market_data = get_market_data('eur', 'usd', year=2023)

market_data = market_data[:10_000]

strategy_0 = indicators.RelativeStrengthIndex()

strategy_1 = indicators.StochRSIIndicator()

strategy_2 = indicators.MovingAverageCrossing()

strategy = Strategy(strategy_0)

strategy.generate_signal(market_data)

strategy.plot()

