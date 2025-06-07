
import numpy as np
from TradeTide.indicators_ import MovingAverageCrossing
from TradeTide.market import Market
from TradeTide.currencies import Currency
from datetime import timedelta
from TradeTide.times import days, minutes

market = Market()



market.load_from_database(
    currency_0=Currency.CAD,
    currency_1=Currency.USD,
    year=2023,
    time_span=1 * days,
)


# Define constants for window sizes
SHORT_WINDOW = 3 * minutes
LONG_WINDOW = 20 * minutes



prices = abs(np.linspace(-1, 1, 100)) + 3
indicator = MovingAverageCrossing(
    short_window=SHORT_WINDOW,
    long_window=LONG_WINDOW
)


indicator.run(market)

indicator.plot()
