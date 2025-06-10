from TradeTide.indicators import MovingAverageCrossing
from TradeTide.market import Market
from TradeTide.currencies import Currency
from TradeTide.times import days, minutes
from TradeTide.market import Market
from TradeTide.currencies import Currency

market = Market()

market.load_from_database(
    currency_0=Currency.CAD,
    currency_1=Currency.USD,
    time_span=3 * days,
)

indicator = MovingAverageCrossing(
    short_window=3 * minutes,
    long_window=5 * minutes,
)

indicator.run(market)

indicator.plot()