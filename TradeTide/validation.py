"""Chronological train/test and walk-forward validation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from TradeTide.execution import ExecutionCosts
from TradeTide.market import Market
from TradeTide.performance import BacktestResult


@dataclass(frozen=True)
class MarketSplit:
    """Non-overlapping chronological train and test markets."""

    train: Market
    test: Market
    split_index: int


@dataclass(frozen=True)
class WalkForwardWindow:
    """Index boundaries for one chronological train/test fold."""

    train_start: int
    train_end: int
    test_start: int
    test_end: int


@dataclass(frozen=True)
class WalkForwardResult:
    """Out-of-sample reports, one for each completed walk-forward fold."""

    windows: tuple[WalkForwardWindow, ...]
    results: tuple[BacktestResult, ...]


def chronological_split(market: Market, train_size: float = 0.7) -> MarketSplit:
    """Split a market into deterministic, non-overlapping train and test periods.

    ``train_size`` is a fraction of observations and must leave at least one
    observation in each period.  No shuffling is performed, preventing future
    observations from leaking into the training data.
    """
    if not 0.0 < train_size < 1.0:
        raise ValueError("train_size must be strictly between 0 and 1.")
    split_index = int(len(market.dates) * train_size)
    if split_index == 0 or split_index >= len(market.dates):
        raise ValueError(
            "train_size must leave at least one observation in each split."
        )
    return MarketSplit(
        train=slice_market(market, 0, split_index),
        test=slice_market(market, split_index, len(market.dates)),
        split_index=split_index,
    )


def slice_market(market: Market, start: int, end: int) -> Market:
    """Copy ``market[start:end]`` into a standalone, valid :class:`Market`."""
    if not 0 <= start < end <= len(market.dates):
        raise ValueError(
            "Market slice bounds must satisfy 0 <= start < end <= len(market)."
        )
    sliced = Market()
    for index in range(start, end):
        sliced.add_market_data(
            market.dates[index],
            market.ask.open[index],
            market.ask.low[index],
            market.ask.high[index],
            market.ask.close[index],
            market.bid.open[index],
            market.bid.low[index],
            market.bid.high[index],
            market.bid.close[index],
        )
    sliced.currency_pair = getattr(market, "currency_pair", None)
    return sliced


class WalkForwardSplitter:
    """Generate fixed or expanding chronological train/test windows.

    Parameters are expressed in market observations.  The output is deterministic
    and never overlaps a fold's train and test regions.
    """

    def __init__(
        self,
        train_size: int,
        test_size: int,
        step_size: int | None = None,
        expanding: bool = True,
    ) -> None:
        if train_size < 2 or test_size < 2:
            raise ValueError("train_size and test_size must each be at least 2.")
        self.train_size = train_size
        self.test_size = test_size
        self.step_size = step_size or test_size
        self.expanding = expanding
        if self.step_size < 1:
            raise ValueError("step_size must be positive.")

    def split(self, market: Market) -> tuple[WalkForwardWindow, ...]:
        """Return every complete fold that fits inside ``market``."""
        windows: list[WalkForwardWindow] = []
        test_start = self.train_size
        while test_start + self.test_size <= len(market.dates):
            train_start = 0 if self.expanding else test_start - self.train_size
            windows.append(
                WalkForwardWindow(
                    train_start=train_start,
                    train_end=test_start,
                    test_start=test_start,
                    test_end=test_start + self.test_size,
                )
            )
            test_start += self.step_size
        if not windows:
            raise ValueError(
                "Market is too short for one complete walk-forward window."
            )
        return tuple(windows)

    def run(
        self,
        market: Market,
        strategy_factory: Callable[[Market], object],
        exit_strategy_factory: Callable[[], object],
        capital_management_factory: Callable[[], object],
        execution_costs: ExecutionCosts | None = None,
    ) -> WalkForwardResult:
        """Run fresh, out-of-sample backtests for every generated test window.

        ``strategy_factory`` receives only the training market.  It must return
        a strategy ready for the test market; this keeps parameter fitting under
        the caller's control while making the test execution strictly isolated.
        """
        from TradeTide.backtester import Backtester

        windows = self.split(market)
        results: list[BacktestResult] = []
        for window in windows:
            training_market = slice_market(market, window.train_start, window.train_end)
            testing_market = slice_market(market, window.test_start, window.test_end)
            strategy = strategy_factory(training_market)
            backtester = Backtester(
                strategy=strategy,
                market=testing_market,
                exit_strategy=exit_strategy_factory(),
                capital_management=capital_management_factory(),
                execution_costs=execution_costs,
            )
            results.append(backtester.run())
        return WalkForwardResult(windows=windows, results=tuple(results))
