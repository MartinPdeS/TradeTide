"""
Bollinger Bands
---------------

This example demonstrates how to use the Bollinger Bands indicator with the TradeTide library.

"""

from TradeTide.indicators import BollingerBands
from TradeTide.market import Market
from TradeTide.currencies import Currency
from TradeTide.times import days, minutes
from TradeTide.market import Market
from TradeTide.currencies import Currency

market = Market()

market.load_from_database(
    currency_0=Currency.CAD,
    currency_1=Currency.USD,
    time_span=30 * minutes,
)

indicator = BollingerBands(
    window=3 * minutes,
    multiplier=2.0
)

indicator.run(market)

indicator.plot()