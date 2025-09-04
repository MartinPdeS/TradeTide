"""
Relative Momentum Index
-----------------------

This example demonstrates how to use the Relative Momentum Index (RMI) indicator

"""

from TradeTide.indicators import RelativeMomentumIndex
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

indicator = RelativeMomentumIndex(
    momentum_period=3 * minutes,
    smooth_window=5 * minutes,
    over_bought=70.0,
    over_sold=30.0,
)

indicator.run(market)

indicator.plot()
