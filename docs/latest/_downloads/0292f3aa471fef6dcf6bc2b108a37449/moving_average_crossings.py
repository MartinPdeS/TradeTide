"""
Moving Average Crossings
------------------------

This example demonstrates how to use the Moving Average Crossings indicator with the TradeTide library.

"""


from TradeTide.indicators import MovingAverageCrossing
from TradeTide.market import Market
from TradeTide.currencies import Currency
from TradeTide.times import minutes
from TradeTide.market import Market
from TradeTide.currencies import Currency

market = Market()

market.load_from_database(
    currency_0=Currency.CAD,
    currency_1=Currency.USD,
    time_span=60 * minutes,
)

indicator = MovingAverageCrossing(
    short_window=3 * minutes,
    long_window=5 * minutes,
)

indicator.run(market)

indicator.plot()