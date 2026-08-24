"""Tests for the batched candlestick renderer."""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pytest

from TradeTide.market import Market


def _market_with_ticks(count: int = 10) -> Market:
    market = Market()
    start = datetime(2024, 1, 1)
    for index in range(count):
        bid = 1.1000 + index * 0.0001
        market.add_tick(start + timedelta(minutes=index), bid + 0.0002, bid)
    return market


def test_candles_are_batched_and_decimated():
    market = _market_with_ticks()
    figure = market.plot_candles(max_candles=3, show=False)
    axes = figure.axes[0]

    # Two wick and two body collections, regardless of the source row count.
    assert len(axes.collections) == 4
    body_count = sum(
        len(collection.get_paths()) for collection in axes.collections[1::2]
    )
    assert body_count == 3
    plt.close(figure)


def test_market_plot_uses_batched_candles_for_both_sides():
    market = _market_with_ticks()
    figure = market.plot(show=False)

    assert len(figure.axes[0].collections) == 8
    plt.close(figure)


def test_candles_validate_maximum_count():
    market = _market_with_ticks()

    with pytest.raises(ValueError, match="max_candles"):
        market.plot_candles(max_candles=0, show=False)
