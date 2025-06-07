
import numpy as np
from TradeTide.indicators import MovingAverageCrossing, BollingerBands
from TradeTide.market import Market
from TradeTide.currencies import Currency
from TradeTide.times import days, minutes

market = Market()



market.load_from_database(
    currency_0=Currency.CAD,
    currency_1=Currency.USD,
    time_span=1 * days,
)



# indicator = MovingAverageCrossing(
#     short_window=3 * minutes,
#     long_window=20 * minutes
# )


# indicator.run(market)

# indicator.plot()

indicator = BollingerBands(
    window=3 * minutes,
    multiplier=2.0
)

indicator.run(market)
indicator.plot()