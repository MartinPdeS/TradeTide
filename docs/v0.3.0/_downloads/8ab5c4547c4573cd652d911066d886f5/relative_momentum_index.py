"""
Relative Momentum Index
-----------------------

This example demonstrates how to use the Relative Momentum Index (RMI) indicator

"""

from TradeTide import RelativeMomentumIndex
from TradeTide import Market
from TradeTide.currencies import Currency
from TradeTide.times import minutes

market = Market()

market.load_from_database(
    currency_0=Currency.CAD,
    currency_1=Currency.USD,
    time_span=30 * minutes,
)

indicator = RelativeMomentumIndex(
    # Native indicators use bar counts rather than timedelta windows.
    momentum_period=3,
    smooth_period=5,
    over_bought=70.0,
    over_sold=30.0,
)

indicator.run(market)

# Display the figure using Matplotlib's configured interactive backend.
figure = indicator.plot()
