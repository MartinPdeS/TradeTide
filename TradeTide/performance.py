"""Structured, reproducible performance reporting for completed backtests."""

from dataclasses import asdict, dataclass
from datetime import datetime
from math import sqrt
from typing import TYPE_CHECKING, Iterable, Mapping

import numpy as np

from TradeTide.execution import ExecutionCosts, TradeCost
from TradeTide.ledger import TradeLedger
from TradeTide.debug import logger

if TYPE_CHECKING:
    from TradeTide import Portfolio


@dataclass(frozen=True)
class PerformanceMetrics:
    """Common portfolio statistics, expressed as decimal fractions where applicable."""

    total_return: float
    annualized_return: float
    volatility: float
    max_drawdown: float
    max_drawdown_duration_seconds: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
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
    exit_reason: str
    maximum_adverse_excursion: float
    maximum_favorable_excursion: float

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
    ledger: TradeLedger

    @classmethod
    def from_portfolio(
        cls,
        portfolio: "Portfolio",
        execution_costs: ExecutionCosts | None = None,
    ) -> "BacktestResult":
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
            exit_reason, mae, mfe = _trade_diagnostics(position, portfolio.market)
            trade = TradeResult(
                entry_time=position.start_date,
                exit_time=position.close_date,
                is_long=position.is_long,
                entry_price=position.entry_price,
                exit_price=position.exit_price,
                lot_size=position.lot_size,
                gross_pnl=gross_pnl,
                costs=trade_cost,
                exit_reason=exit_reason,
                maximum_adverse_excursion=mae,
                maximum_favorable_excursion=mfe,
            )
            trades.append(trade)
            logger.debug(
                "Trade %s %s→%s gross=%.4f costs=%.4f net=%.4f (%s)",
                "long" if trade.is_long else "short",
                trade.entry_time,
                trade.exit_time,
                trade.gross_pnl,
                trade.costs.total,
                trade.net_pnl,
                trade.exit_reason,
            )
            cost_events.extend(costs.cashflow_events(position, trade_cost))

        net_equity = _apply_cost_events(times, gross_equity, cost_events)
        metrics = _calculate_metrics(net_equity, times, trades)
        ledger = TradeLedger.from_trades(tuple(trades))
        logger.debug(
            "Backtest report: observations=%d trades=%d return=%.2f%% max_drawdown=%.2f%%",
            len(times),
            len(trades),
            metrics.total_return * 100,
            metrics.max_drawdown * 100,
        )
        return cls(
            times=times,
            equity=tuple(float(value) for value in net_equity),
            trades=tuple(trades),
            metrics=metrics,
            execution_costs=costs,
            ledger=ledger,
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
                    "costs": {
                        "commission": trade.costs.commission,
                        "slippage": trade.costs.slippage,
                        "spread": trade.costs.spread,
                        "financing": trade.costs.financing,
                    },
                    "exit_reason": trade.exit_reason,
                    "maximum_adverse_excursion": trade.maximum_adverse_excursion,
                    "maximum_favorable_excursion": trade.maximum_favorable_excursion,
                }
                for trade in self.trades
            ],
        }

    def plot_equity_drawdown(self, **kwargs):
        """Plot net equity as candles with a synchronized drawdown panel."""
        return plot_equity_drawdown(self, **kwargs)


def _trade_diagnostics(position, market) -> tuple[str, float, float]:
    """Classify a native position's exit and calculate MAE/MFE from OHLC data."""
    if not all(hasattr(market, attribute) for attribute in ("dates", "ask", "bid")):
        return _classify_exit(position, False), 0.0, 0.0
    dates = list(market.dates)
    start = dates.index(position.start_date)
    end = dates.index(position.close_date)
    if position.is_long:
        lows = np.asarray(market.bid.low[start : end + 1], dtype=float)
        highs = np.asarray(market.bid.high[start : end + 1], dtype=float)
        mae = (lows.min() - position.entry_price) * position.lot_size
        mfe = (highs.max() - position.entry_price) * position.lot_size
    else:
        lows = np.asarray(market.ask.low[start : end + 1], dtype=float)
        highs = np.asarray(market.ask.high[start : end + 1], dtype=float)
        mae = (position.entry_price - highs.max()) * position.lot_size
        mfe = (position.entry_price - lows.min()) * position.lot_size
    return _classify_exit(position, end == len(dates) - 1), float(mae), float(mfe)


def _classify_exit(position, reached_end_of_data: bool) -> str:
    if reached_end_of_data:
        return "end_of_data"
    if position.get_price_difference() > 0:
        return "take_profit"
    if position.get_price_difference() < 0:
        return "stop_loss"
    return "break_even"


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
    downside_std = (
        float(np.sqrt(np.mean(np.square(downside)))) if downside.size else 0.0
    )
    sortino = (
        mean_return / downside_std * sqrt(periods_per_year) if downside_std else 0.0
    )
    peaks = np.maximum.accumulate(equity)
    drawdown = np.divide(
        equity - peaks, peaks, out=np.zeros_like(equity), where=peaks != 0
    )
    max_drawdown = float(-drawdown.min())
    duration_seconds = (times[-1] - times[0]).total_seconds() if len(times) > 1 else 0.0
    annualized = (
        (1.0 + total_return) ** (365.25 * 86_400 / duration_seconds) - 1.0
        if duration_seconds and final > 0
        else 0.0
    )
    calmar = annualized / max_drawdown if max_drawdown else 0.0
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
        max_drawdown=max_drawdown,
        max_drawdown_duration_seconds=_max_drawdown_duration(times, drawdown),
        sharpe_ratio=sharpe,
        sortino_ratio=sortino,
        calmar_ratio=calmar,
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


def _max_drawdown_duration(times: tuple[datetime, ...], drawdown: np.ndarray) -> float:
    """Return the longest peak-to-recovery interval in seconds."""
    start: datetime | None = None
    longest = 0.0
    for time, value in zip(times, drawdown):
        if value < 0 and start is None:
            start = time
        elif value >= 0 and start is not None:
            longest = max(longest, (time - start).total_seconds())
            start = None
    if start is not None and times:
        longest = max(longest, (times[-1] - start).total_seconds())
    return longest


def plot_equity_drawdown(
    result: BacktestResult,
    *,
    axes=None,
    show: bool = True,
    max_candles: int = 500,
):
    """Plot a backtest's net equity as candles and its drawdown below.

    Equity candles use the previous equity as each candle's open and the current
    equity as its close.  They preserve the visual language of the market chart
    while making individual-period gains and losses immediately visible.
    """
    if max_candles < 1:
        raise ValueError("max_candles must be a positive integer.")

    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection, PolyCollection
    from matplotlib.dates import date2num

    times = np.asarray(result.times)
    equity = np.asarray(result.equity, dtype=float)
    if len(times) != len(equity) or not len(times):
        raise ValueError(
            "A result must contain equally sized, non-empty time and equity data."
        )
    if len(times) > max_candles:
        groups = np.array_split(np.arange(len(times)), max_candles)
        times = np.asarray([times[group[-1]] for group in groups])
        equity = np.asarray([equity[group[-1]] for group in groups], dtype=float)

    if axes is None:
        figure, axes = plt.subplots(2, 1, sharex=True, height_ratios=(3, 1))
    else:
        axes = np.asarray(axes).ravel()
        if len(axes) != 2:
            raise ValueError("axes must contain exactly two Matplotlib axes.")
        figure = axes[0].figure
    equity_axis, drawdown_axis = axes

    x_values = date2num(times)
    opens = np.concatenate(([equity[0]], equity[:-1]))
    highs = np.maximum(opens, equity)
    lows = np.minimum(opens, equity)
    interval = np.median(np.diff(x_values)) if len(x_values) > 1 else 1.0
    width = interval * 0.7
    rising = equity >= opens
    colors = np.where(rising, "#19a974", "#e05263")
    wicks = LineCollection(
        [((x, low), (x, high)) for x, low, high in zip(x_values, lows, highs)],
        colors=colors,
        linewidths=0.8,
    )
    bodies = PolyCollection(
        [
            (
                (x - width / 2, opening),
                (x - width / 2, closing),
                (x + width / 2, closing),
                (x + width / 2, opening),
            )
            for x, opening, closing in zip(x_values, opens, equity)
        ],
        facecolors=colors,
        edgecolors=colors,
        linewidths=0.5,
    )
    equity_axis.add_collection(wicks)
    equity_axis.add_collection(bodies)
    equity_axis.autoscale_view()
    equity_axis.axhline(
        result.metrics.initial_equity, color="#64748b", linestyle="--", linewidth=0.8
    )
    equity_axis.set_ylabel("Net equity")
    equity_axis.set_title("Equity candles")

    peaks = np.maximum.accumulate(equity)
    drawdown = (
        np.divide(equity - peaks, peaks, out=np.zeros_like(equity), where=peaks != 0)
        * 100
    )
    drawdown_axis.fill_between(times, drawdown, 0, color="#e05263", alpha=0.25)
    drawdown_axis.plot(times, drawdown, color="#e05263", linewidth=1)
    drawdown_axis.set_ylabel("Drawdown (%)")
    drawdown_axis.set_xlabel("Time")
    drawdown_axis.set_title(f"Maximum drawdown: {result.metrics.max_drawdown:.2%}")
    figure.tight_layout()
    if show:
        plt.show()
    return figure
