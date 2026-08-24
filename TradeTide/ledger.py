"""Trade-level ledger and position analytics."""

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from TradeTide.performance import TradeResult


@dataclass(frozen=True)
class LedgerEntry:
    """A completed trade ready for audit, export, or post-trade analysis."""

    trade_id: int
    entry_time: datetime
    exit_time: datetime
    side: str
    entry_price: float
    exit_price: float
    lot_size: float
    gross_pnl: float
    net_pnl: float
    total_cost: float
    exit_reason: str
    holding_period: timedelta
    maximum_adverse_excursion: float
    maximum_favorable_excursion: float


@dataclass(frozen=True)
class PositionAnalytics:
    """Summary statistics derived from the complete trade ledger."""

    long_trades: int
    short_trades: int
    average_holding_period: timedelta
    expectancy: float
    average_win: float
    average_loss: float
    longest_winning_streak: int
    longest_losing_streak: int
    average_mae: float
    average_mfe: float
    best_trade: float
    worst_trade: float


@dataclass(frozen=True)
class TradeLedger:
    """Immutable ledger with convenient dictionary and dataframe exports."""

    entries: tuple[LedgerEntry, ...]
    analytics: PositionAnalytics

    @classmethod
    def from_trades(
        cls, trades: "tuple[TradeResult, ...]"
    ) -> "TradeLedger":
        entries = tuple(
            LedgerEntry(
                trade_id=index + 1,
                entry_time=trade.entry_time,
                exit_time=trade.exit_time,
                side="long" if trade.is_long else "short",
                entry_price=trade.entry_price,
                exit_price=trade.exit_price,
                lot_size=trade.lot_size,
                gross_pnl=trade.gross_pnl,
                net_pnl=trade.net_pnl,
                total_cost=trade.costs.total,
                exit_reason=trade.exit_reason,
                holding_period=trade.exit_time - trade.entry_time,
                maximum_adverse_excursion=trade.maximum_adverse_excursion,
                maximum_favorable_excursion=trade.maximum_favorable_excursion,
            )
            for index, trade in enumerate(trades)
        )
        return cls(entries=entries, analytics=_analyse(entries))

    def to_dicts(self) -> list[dict[str, object]]:
        """Return serializable rows, one for every completed trade."""
        return [asdict(entry) for entry in self.entries]

    def to_dataframe(self):
        """Return a pandas dataframe without making pandas part of the core API."""
        import pandas as pd

        return pd.DataFrame(self.to_dicts())


def _analyse(entries: tuple[LedgerEntry, ...]) -> PositionAnalytics:
    pnls = np.asarray([entry.net_pnl for entry in entries], dtype=float)
    winners = pnls[pnls > 0]
    losers = pnls[pnls < 0]
    durations = [entry.holding_period for entry in entries]
    average_duration = (
        sum(durations, timedelta()) / len(durations) if durations else timedelta()
    )
    return PositionAnalytics(
        long_trades=sum(entry.side == "long" for entry in entries),
        short_trades=sum(entry.side == "short" for entry in entries),
        average_holding_period=average_duration,
        expectancy=float(pnls.mean()) if pnls.size else 0.0,
        average_win=float(winners.mean()) if winners.size else 0.0,
        average_loss=float(losers.mean()) if losers.size else 0.0,
        longest_winning_streak=_longest_streak(pnls, positive=True),
        longest_losing_streak=_longest_streak(pnls, positive=False),
        average_mae=float(
            np.mean([entry.maximum_adverse_excursion for entry in entries])
        )
        if entries
        else 0.0,
        average_mfe=float(
            np.mean([entry.maximum_favorable_excursion for entry in entries])
        )
        if entries
        else 0.0,
        best_trade=float(pnls.max()) if pnls.size else 0.0,
        worst_trade=float(pnls.min()) if pnls.size else 0.0,
    )


def _longest_streak(pnls: np.ndarray, positive: bool) -> int:
    longest = current = 0
    for pnl in pnls:
        matches = pnl > 0 if positive else pnl < 0
        current = current + 1 if matches else 0
        longest = max(longest, current)
    return longest
