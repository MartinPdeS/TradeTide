"""Matplotlib rendering helpers for the native :class:`TradeTide.Market`."""

from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.dates import date2num

from TradeTide.plotting import pre_plot


def _aggregate(market, side: str, max_candles: int | None):
    prices = market.ask if side == "ask" else market.bid
    dates = np.asarray(market.dates)
    opening = np.asarray(prices.open, dtype=float)
    low = np.asarray(prices.low, dtype=float)
    high = np.asarray(prices.high, dtype=float)
    closing = np.asarray(prices.close, dtype=float)
    if max_candles is None or len(dates) <= max_candles:
        return dates, opening, low, high, closing
    if max_candles < 1:
        raise ValueError("max_candles must be a positive integer or None.")
    groups = np.array_split(np.arange(len(dates)), max_candles)
    return (
        np.asarray([dates[group[0]] for group in groups]),
        np.asarray([opening[group[0]] for group in groups]),
        np.asarray([low[group].min() for group in groups]),
        np.asarray([high[group].max() for group in groups]),
        np.asarray([closing[group[-1]] for group in groups]),
    )


@pre_plot()
def plot_market_candles(
    market,
    axes: plt.Axes,
    side: Literal["ask", "bid"] = "ask",
    max_candles: int | None = 2_000,
) -> None:
    """Render batched OHLC candles for a native market object."""
    if side not in ("ask", "bid"):
        raise ValueError("side must be either 'ask' or 'bid'.")
    dates, opening, low, high, closing = _aggregate(market, side, max_candles)
    if not len(dates):
        return
    x = date2num(dates)
    spacing = np.diff(x)
    width = (
        np.median(spacing[spacing > 0]) if np.any(spacing > 0) else 1 / 1_440
    ) * 0.7
    rising = closing >= opening
    for mask, color, label in ((rising, "#16a085", "up"), (~rising, "#e74c3c", "down")):
        values, opens, closes, lows, highs = (
            x[mask],
            opening[mask],
            closing[mask],
            low[mask],
            high[mask],
        )
        axes.add_collection(
            LineCollection(
                np.stack(
                    (np.column_stack((values, lows)), np.column_stack((values, highs))),
                    axis=1,
                ),
                colors=color,
                linewidths=0.8,
            )
        )
        axes.add_collection(
            PolyCollection(
                [
                    (
                        (value - width / 2, opened),
                        (value + width / 2, opened),
                        (value + width / 2, closed),
                        (value - width / 2, closed),
                    )
                    for value, opened, closed in zip(values, opens, closes)
                ],
                facecolors=color,
                edgecolors=color,
                linewidths=0.5,
                label=f"{side} {label}",
            )
        )
    axes.autoscale_view()
    axes.set_xlabel("Time")
    axes.set_ylabel("Price")
    axes.set_title(f"{market.currency_pair} - {market.time_span}")
    axes.legend(loc="upper left")


@pre_plot()
def plot_market(market, axes: plt.Axes, max_candles: int | None = 2_000) -> None:
    """Render batched ask and bid candles on one axes."""
    plot_market_candles(
        market, axes=axes, side="ask", max_candles=max_candles, show=False
    )
    plot_market_candles(
        market, axes=axes, side="bid", max_candles=max_candles, show=False
    )
