"""
Moving Average Crossings
------------------------

This example demonstrates how to use the Moving Average Crossings indicator with the TradeTide library.

"""
import numpy as np

from TradeTide.indicators import MovingAverageCrossing
from TradeTide.market import Market
from TradeTide.currencies import Currency
from TradeTide.times import minutes, hours
from TradeTide.market import Market
from TradeTide.currencies import Currency

market = Market()

market.load_from_database(
    currency_0=Currency.CAD,
    currency_1=Currency.USD,
    time_span=60 * minutes,
)

data = np.arange(100, 200, 1.0)

indicator = MovingAverageCrossing(
    short_window=3 * minutes,
    long_window=1 * hours,
)

indicator._cpp_run_with_vector(data)


print(indicator._cpp_short_moving_average)


# indicator.run(market)

# indicator.plot()