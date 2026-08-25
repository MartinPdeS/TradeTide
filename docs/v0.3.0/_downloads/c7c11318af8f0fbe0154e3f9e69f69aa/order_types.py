"""
Order Types and Deterministic Fills
===================================

``OrderBook`` evaluates market, limit, stop, and stop-limit entry orders
against bid/ask OHLC data.  It records the fill time, bar index, and execution
price, and can produce an entry signal compatible with ``PositionCollection``.
"""

# %%
# Build a tiny deterministic market.  The first candle crosses the prices used
# below, making the outcome easy to inspect.

from datetime import datetime, timedelta

from TradeTide import Market, Order, OrderBook, OrderSide, OrderType

market = Market()
start = datetime(2024, 1, 1, 9)
market.add_market_data(
    start,
    1.2000,  # ask open
    1.4000,  # ask high
    0.9000,  # ask low
    1.2000,  # ask close
    1.1998,  # bid open
    1.3998,  # bid high
    0.8998,  # bid low
    1.1998,  # bid close
)
market.add_tick(start + timedelta(minutes=1), ask_price=1.2002, bid_price=1.2000)

# %%
# Place several orders.  A buy limit receives its limit price or a better open;
# a buy stop receives its stop price or a worse open.  A stop-limit first arms
# at the stop, then requires its limit to be reached.

orders = [
    Order("market", OrderSide.BUY, OrderType.MARKET, start),
    Order("limit", OrderSide.BUY, OrderType.LIMIT, start, limit_price=1.0000),
    Order("stop", OrderSide.BUY, OrderType.STOP, start, stop_price=1.3000),
    Order(
        "stop-limit",
        OrderSide.BUY,
        OrderType.STOP_LIMIT,
        start,
        stop_price=1.3000,
        limit_price=0.9500,
    ),
]

book = OrderBook(orders)
fills = book.process(market)

for fill in fills:
    print(f"{fill.order_id:10} {fill.time:%H:%M}  {fill.price:.4f}")

# %%
# Convert fills into a long/short entry stream when connecting the order engine
# to the existing native position workflow.

signals = book.trade_signals(market)
print(signals)
