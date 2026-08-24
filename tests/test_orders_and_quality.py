"""Tests for order triggering, trade analytics, and market-data checks."""

from datetime import datetime, timedelta
from types import SimpleNamespace
import pytest

from TradeTide import Market, Order, OrderBook, OrderSide, OrderStatus, OrderType, TradeLedger
from TradeTide.data_quality import IssueSeverity, validate_market_data
from TradeTide.execution import TradeCost
from TradeTide.performance import TradeResult


def _market() -> Market:
    start = datetime(2024, 1, 1)
    market = Market()
    for index, values in enumerate(
        (
            (1.20, 1.40, 0.90, 1.20, 1.19, 1.39, 0.89, 1.19),
            (1.20, 1.25, 1.10, 1.20, 1.19, 1.24, 1.09, 1.19),
            (1.20, 1.25, 1.10, 1.20, 1.19, 1.24, 1.09, 1.19),
        )
    ):
        market.add_market_data(start + timedelta(minutes=index), *values)
    return market


def _quality_market() -> SimpleNamespace:
    """Mutable fixture for Python-side data-quality validation."""
    start = datetime(2024, 1, 1)
    ask = SimpleNamespace(
        open=[1.20, 1.20, 1.20],
        low=[0.90, 1.10, 1.10],
        high=[1.40, 1.25, 1.25],
        close=[1.20, 1.20, 1.20],
    )
    bid = SimpleNamespace(
        open=[1.19, 1.19, 1.19],
        low=[0.89, 1.09, 1.09],
        high=[1.39, 1.24, 1.24],
        close=[1.19, 1.19, 1.19],
    )
    return SimpleNamespace(
        dates=[start + timedelta(minutes=index) for index in range(3)], ask=ask, bid=bid
    )


def test_order_book_fills_market_limit_stop_and_stop_limit_orders():
    market = _market()
    orders = [
        Order("market", OrderSide.BUY, OrderType.MARKET, market.dates[0]),
        Order(
            "limit", OrderSide.BUY, OrderType.LIMIT, market.dates[0], limit_price=1.00
        ),
        Order("stop", OrderSide.BUY, OrderType.STOP, market.dates[0], stop_price=1.30),
        Order(
            "stop-limit",
            OrderSide.BUY,
            OrderType.STOP_LIMIT,
            market.dates[0],
            stop_price=1.30,
            limit_price=0.95,
        ),
    ]

    fills = OrderBook(orders).process(market)

    assert [fill.order_id for fill in fills] == [
        "market",
        "limit",
        "stop",
        "stop-limit",
    ]
    assert [fill.price for fill in fills] == pytest.approx([1.20, 1.00, 1.30, 0.95])


def test_order_cancellation_expiry_and_signals_are_deterministic():
    market = _market()
    book = OrderBook()
    book.place(Order("sell", OrderSide.SELL, OrderType.MARKET, market.dates[1]))
    expired = book.place(
        Order(
            "old",
            OrderSide.BUY,
            OrderType.LIMIT,
            market.dates[0],
            limit_price=0.50,
            expires_at=market.dates[0],
        )
    )
    book.cancel("old")

    signals = book.trade_signals(market)

    assert signals.tolist() == [0, -1, 0]
    assert expired.status == OrderStatus.CANCELLED


def test_market_validation_reports_timestamp_and_spread_problems():
    market = _quality_market()
    market.dates[1] = market.dates[0]
    market.ask.close[0] = 1.50

    report = validate_market_data(market, max_spread_ratio=0.01)

    assert not report.valid
    assert any(issue.code == "timestamp_order" for issue in report.errors)
    assert any(issue.severity is IssueSeverity.WARNING for issue in report.warnings)
    with pytest.raises(ValueError, match="validation failed"):
        report.raise_for_errors()


def test_trade_ledger_calculates_position_analytics():
    start = datetime(2024, 1, 1)
    trades = (
        TradeResult(
            start,
            start + timedelta(hours=1),
            True,
            1.0,
            1.1,
            10,
            1.0,
            TradeCost(),
            "take_profit",
            -0.2,
            1.2,
        ),
        TradeResult(
            start,
            start + timedelta(hours=2),
            False,
            1.1,
            1.2,
            10,
            -1.0,
            TradeCost(),
            "stop_loss",
            -1.1,
            0.2,
        ),
    )

    ledger = TradeLedger.from_trades(trades)

    assert ledger.analytics.long_trades == 1
    assert ledger.analytics.short_trades == 1
    assert ledger.analytics.expectancy == pytest.approx(0.0)
    assert ledger.analytics.longest_winning_streak == 1
    assert ledger.analytics.longest_losing_streak == 1
    assert ledger.entries[0].exit_reason == "take_profit"
