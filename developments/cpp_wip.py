from TradeTide.binaries.interface import Position
from TradeTide import BackTester, indicators, get_market_data, Strategy
from TradeTide import capital_managment, risk_management

market_data = get_market_data('eur', 'usd', year=2023, time_span='10 days', spread=0)
market_data = market_data[:10]
a = market_data.columns
date = market_data.index[0]

pos = Position(start_date=date, market=market_data)
print("Start date:", pos.start_date)