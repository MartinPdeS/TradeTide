"""Structured, reproducible performance reporting for completed backtests."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from math import sqrt
from typing import TYPE_CHECKING, Iterable, Mapping

import numpy as np

from TradeTide.execution import ExecutionCosts, TradeCost

if TYPE_CHECKING:
    from TradeTide.portfolio import Portfolio


@dataclass(frozen=True)
class PerformanceMetrics:
    """Common portfolio statistics, expressed as decimal fractions where applicable."""

    total_return: float
    annualized_return: float
    volatility: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    win_rate: float
    profit_factor: float
    exposure: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    initial_equity: float
    final_equity: float
    peak_equity: float

    def to_dict(self) -> dict[str, float | int]:
        """Return JSON- and dataframe-friendly metric values."""
        return asdict(self)


@dataclass(frozen=True)
class TradeResult:
    """A completed trade together with its gross and net profit/loss."""

    entry_time: datetime
    exit_time: datetime
    is_long: bool
    entry_price: float
    exit_price: float
    lot_size: float
    gross_pnl: float
    costs: TradeCost

    @property
    def net_pnl(self) -> float:
        """Profit/loss after configured execution costs."""
        return self.gross_pnl - self.costs.total


@dataclass(frozen=True)
class BacktestResult:
    """Immutable report for a completed portfolio simulation.

    ``equity`` is net of the supplied :class:`~TradeTide.execution.ExecutionCosts`.
    With the default no-cost model it exactly matches the portfolio's recorded equity.
    """

    times: tuple[datetime, ...]
    equity: tuple[float, ...]
    trades: tuple[TradeResult, ...]
    metrics: PerformanceMetrics
    execution_costs: ExecutionCosts

    @classmethod
    def from_portfolio(
        cls,
        portfolio: Portfolio,
        execution_costs: ExecutionCosts | None = None,
    ) -> BacktestResult:
        """Build a net performance report from an already simulated portfolio."""
        costs = execution_costs or ExecutionCosts()
        times = tuple(portfolio.record.time)
        gross_equity = np.asarray(portfolio.record.equity, dtype=float)
        if not times or gross_equity.size != len(times):
            raise RuntimeError(
                "Portfolio has no completed simulation record. Call simulate() first."
            )

        cost_events: list[tuple[datetime, float]] = []
        trades: list[TradeResult] = []
        for position in portfolio.get_positions():
            trade_cost = costs.for_trade(position, portfolio.market.pip_value)
            gross_pnl = position.get_price_difference() * position.lot_size
            trade = TradeResult(
                entry_time=position.start_date,
                exit_time=position.close_date,
                is_long=position.is_long,
                entry_price=position.entry_price,
                exit_price=position.exit_price,
                lot_size=position.lot_size,
                gross_pnl=gross_pnl,
                costs=trade_cost,
            )
            trades.append(trade)
            cost_events.extend(costs.cashflow_events(position, trade_cost))

        net_equity = _apply_cost_events(times, gross_equity, cost_events)
        metrics = _calculate_metrics(net_equity, times, trades)
        return cls(
            times=times,
            equity=tuple(float(value) for value in net_equity),
            trades=tuple(trades),
            metrics=metrics,
            execution_costs=costs,
        )

    def to_dict(self) -> Mapping[str, object]:
        """Return a serializable report with metrics, equity, and trade details."""
        return {
            "metrics": self.metrics.to_dict(),
            "equity": list(self.equity),
            "times": list(self.times),
            "trades": [
                {
                    "entry_time": trade.entry_time,
                    "exit_time": trade.exit_time,
                    "is_long": trade.is_long,
                    "entry_price": trade.entry_price,
                    "exit_price": trade.exit_price,
                    "lot_size": trade.lot_size,
                    "gross_pnl": trade.gross_pnl,
                    "net_pnl": trade.net_pnl,
                    "costs": asdict(trade.costs),
                }
                for trade in self.trades
            ],
        }


def _apply_cost_events(
    times: tuple[datetime, ...],
    gross_equity: np.ndarray,
    events: Iterable[tuple[datetime, float]],
) -> np.ndarray:
    cumulative_costs = np.zeros(len(times), dtype=float)
    for event_time, amount in events:
        if amount == 0:
            continue
        index = next((i for i, time in enumerate(times) if time >= event_time), None)
        if index is not None:
            cumulative_costs[index:] += amount
    return gross_equity - cumulative_costs


def _calculate_metrics(
    equity: np.ndarray,
    times: tuple[datetime, ...],
    trades: list[TradeResult],
) -> PerformanceMetrics:
    initial = float(equity[0])
    final = float(equity[-1])
    total_return = final / initial - 1.0 if initial else 0.0
    valid_equity = np.where(equity > 0, equity, np.nan)
    returns = np.diff(valid_equity) / valid_equity[:-1]
    returns = returns[np.isfinite(returns)]
    periods_per_year = _periods_per_year(times)
    volatility = (
        float(np.std(returns, ddof=1) * sqrt(periods_per_year))
        if returns.size > 1
        else 0.0
    )
    mean_return = float(np.mean(returns)) if returns.size else 0.0
    return_std = float(np.std(returns, ddof=1)) if returns.size > 1 else 0.0
    sharpe = mean_return / return_std * sqrt(periods_per_year) if return_std else 0.0
    downside = returns[returns < 0]
    downside_std = float(np.std(downside, ddof=1)) if downside.size > 1 else 0.0
    sortino = (
        mean_return / downside_std * sqrt(periods_per_year) if downside_std else 0.0
    )
    peaks = np.maximum.accumulate(equity)
    drawdown = np.divide(
        equity - peaks, peaks, out=np.zeros_like(equity), where=peaks != 0
    )
    duration_seconds = (times[-1] - times[0]).total_seconds() if len(times) > 1 else 0.0
    annualized = (
        (1.0 + total_return) ** (365.25 * 86_400 / duration_seconds) - 1.0
        if duration_seconds and final > 0
        else 0.0
    )
    net_pnls = np.asarray([trade.net_pnl for trade in trades], dtype=float)
    wins = int(np.count_nonzero(net_pnls > 0))
    losses = int(np.count_nonzero(net_pnls < 0))
    gross_profit = float(net_pnls[net_pnls > 0].sum())
    gross_loss = float(-net_pnls[net_pnls < 0].sum())
    profit_factor = (
        gross_profit / gross_loss
        if gross_loss
        else (float("inf") if gross_profit else 0.0)
    )
    exposure = _exposure(times, trades)
    return PerformanceMetrics(
        total_return=total_return,
        annualized_return=annualized,
        volatility=volatility,
        max_drawdown=float(-drawdown.min()),
        sharpe_ratio=sharpe,
        sortino_ratio=sortino,
        win_rate=wins / len(trades) if trades else 0.0,
        profit_factor=profit_factor,
        exposure=exposure,
        total_trades=len(trades),
        winning_trades=wins,
        losing_trades=losses,
        initial_equity=initial,
        final_equity=final,
        peak_equity=float(peaks.max()),
    )


def _periods_per_year(times: tuple[datetime, ...]) -> float:
    if len(times) < 2:
        return 1.0
    intervals = np.asarray(
        [(right - left).total_seconds() for left, right in zip(times, times[1:])]
    )
    interval = (
        float(np.median(intervals[intervals > 0])) if np.any(intervals > 0) else 0.0
    )
    return 365.25 * 86_400 / interval if interval else 1.0


def _exposure(times: tuple[datetime, ...], trades: list[TradeResult]) -> float:
    if len(times) < 2:
        return 0.0
    total_seconds = (times[-1] - times[0]).total_seconds()
    if total_seconds <= 0:
        return 0.0
    intervals = sorted((trade.entry_time, trade.exit_time) for trade in trades)
    merged: list[list[datetime]] = []
    for start, end in intervals:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        elif end > merged[-1][1]:
            merged[-1][1] = end
    active_seconds = sum((end - start).total_seconds() for start, end in merged)
    return min(max(active_seconds / total_seconds, 0.0), 1.0)
