"""Deterministic OHLC order triggering for market, limit, and stop orders."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

import numpy as np

from TradeTide.debug import logger

if TYPE_CHECKING:
    from TradeTide import Market


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class Order:
    """An entry order evaluated against a market's bid/ask OHLC data."""

    order_id: str
    side: OrderSide
    order_type: OrderType
    submitted_at: datetime
    limit_price: float | None = None
    stop_price: float | None = None
    expires_at: datetime | None = None
    status: OrderStatus = field(default=OrderStatus.PENDING, init=False)
    stop_triggered: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if self.order_type is OrderType.LIMIT and self.limit_price is None:
            raise ValueError("Limit orders require limit_price.")
        if self.order_type is OrderType.STOP and self.stop_price is None:
            raise ValueError("Stop orders require stop_price.")
        if self.order_type is OrderType.STOP_LIMIT and (
            self.stop_price is None or self.limit_price is None
        ):
            raise ValueError("Stop-limit orders require stop_price and limit_price.")
        if any(
            value is not None and value <= 0
            for value in (self.limit_price, self.stop_price)
        ):
            raise ValueError("Order prices must be positive.")
        if self.expires_at is not None and self.expires_at < self.submitted_at:
            raise ValueError("expires_at cannot be before submitted_at.")


@dataclass(frozen=True)
class OrderFill:
    """A triggered order with the market observation and fill price used."""

    order_id: str
    side: OrderSide
    order_type: OrderType
    time: datetime
    index: int
    price: float


class OrderBook:
    """Evaluate orders deterministically without assuming intrabar tick order.

    Limit orders receive their requested price or a better opening price. Stop
    orders receive their stop price or a worse opening price. For a stop-limit
    order, the stop must trigger before its limit may fill; when both thresholds
    occur in the same candle, the order fills in that candle.
    """

    def __init__(self, orders: list[Order] | None = None) -> None:
        self.orders = list(orders or [])
        self.fills: list[OrderFill] = []

    def place(self, order: Order) -> Order:
        """Add a pending order, rejecting duplicate identifiers."""
        if any(existing.order_id == order.order_id for existing in self.orders):
            raise ValueError(f"Duplicate order_id: {order.order_id!r}.")
        self.orders.append(order)
        logger.debug(
            "Order accepted: id=%s side=%s type=%s submitted=%s",
            order.order_id,
            order.side.value,
            order.order_type.value,
            order.submitted_at,
        )
        return order

    def cancel(self, order_id: str) -> None:
        """Cancel a pending order by identifier."""
        for order in self.orders:
            if order.order_id == order_id:
                if order.status is OrderStatus.PENDING:
                    order.status = OrderStatus.CANCELLED
                    logger.debug("Order cancelled: id=%s", order_id)
                return
        raise KeyError(f"Unknown order_id: {order_id!r}.")

    def process(self, market: "Market") -> tuple[OrderFill, ...]:
        """Process all pending orders against market OHLC observations."""
        for index, time in enumerate(market.dates):
            for order in self.orders:
                if order.status is not OrderStatus.PENDING or time < order.submitted_at:
                    continue
                if order.expires_at is not None and time > order.expires_at:
                    order.status = OrderStatus.EXPIRED
                    logger.debug("Order expired: id=%s time=%s", order.order_id, time)
                    continue
                fill_price = self._fill_price(order, market, index)
                if fill_price is not None:
                    order.status = OrderStatus.FILLED
                    fill = OrderFill(
                        order_id=order.order_id,
                        side=order.side,
                        order_type=order.order_type,
                        time=time,
                        index=index,
                        price=fill_price,
                    )
                    self.fills.append(fill)
                    logger.debug(
                        "Order filled: id=%s side=%s type=%s index=%d price=%.8f",
                        fill.order_id,
                        fill.side.value,
                        fill.order_type.value,
                        fill.index,
                        fill.price,
                    )
        return tuple(self.fills)

    def trade_signals(self, market: "Market") -> np.ndarray:
        """Return a native-compatible entry signal stream from processed fills."""
        fills = self.process(market)
        signals = np.zeros(len(market.dates), dtype=int)
        for fill in fills:
            signals[fill.index] = 1 if fill.side is OrderSide.BUY else -1
        return signals

    @staticmethod
    def _fill_price(order: Order, market: "Market", index: int) -> float | None:
        prices = market.ask if order.side is OrderSide.BUY else market.bid
        opening, low, high = prices.open[index], prices.low[index], prices.high[index]
        if order.order_type is OrderType.MARKET:
            return opening
        if order.order_type is OrderType.LIMIT or (
            order.order_type is OrderType.STOP_LIMIT and order.stop_triggered
        ):
            assert order.limit_price is not None
            reached = (
                low <= order.limit_price
                if order.side is OrderSide.BUY
                else high >= order.limit_price
            )
            if reached:
                return (
                    min(opening, order.limit_price)
                    if order.side is OrderSide.BUY
                    else max(opening, order.limit_price)
                )
            return None
        assert order.stop_price is not None
        reached = (
            high >= order.stop_price
            if order.side is OrderSide.BUY
            else low <= order.stop_price
        )
        if not reached:
            return None
        if order.order_type is OrderType.STOP_LIMIT:
            order.stop_triggered = True
            return OrderBook._fill_price(order, market, index)
        return (
            max(opening, order.stop_price)
            if order.side is OrderSide.BUY
            else min(opening, order.stop_price)
        )
