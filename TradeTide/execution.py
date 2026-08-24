"""Transparent post-trade execution-cost modelling."""

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from TradeTide.binary.position import BasePosition


@dataclass(frozen=True)
class TradeCost:
    """Cost components for one completed position."""

    commission: float = 0.0
    slippage: float = 0.0
    spread: float = 0.0
    financing: float = 0.0

    @property
    def total(self) -> float:
        """Total all-in cost for the trade."""
        return self.commission + self.slippage + self.spread + self.financing


@dataclass(frozen=True)
class ExecutionCosts:
    """Costs applied to reporting without mutating the native simulation.

    The market's bid/ask prices already represent its recorded spread.  Therefore
    ``extra_spread_pips`` models only *additional* spread.  Commission and
    slippage are charged per side; financing is charged once per completed
    overnight period.  All amounts are in the quote currency of the market.
    """

    commission_per_lot: float = 0.0
    slippage_pips: float = 0.0
    extra_spread_pips: float = 0.0
    financing_per_lot_per_night: float = 0.0

    def __post_init__(self) -> None:
        if any(
            value < 0
            for value in (
                self.commission_per_lot,
                self.slippage_pips,
                self.extra_spread_pips,
                self.financing_per_lot_per_night,
            )
        ):
            raise ValueError("Execution costs must be non-negative.")

    def for_trade(self, position: "BasePosition", pip_value: float) -> TradeCost:
        """Calculate all costs for a position using its actual duration and size."""
        lot_size = position.lot_size
        nights = max((position.close_date - position.start_date).days, 0)
        return TradeCost(
            commission=2.0 * self.commission_per_lot * lot_size,
            slippage=2.0 * self.slippage_pips * pip_value * lot_size,
            spread=self.extra_spread_pips * pip_value * lot_size,
            financing=nights * self.financing_per_lot_per_night * lot_size,
        )

    def cashflow_events(
        self, position: "BasePosition", trade_cost: TradeCost
    ) -> list[tuple[object, float]]:
        """Return entry, overnight, and exit charges for a net equity curve."""
        entry_cost = (
            trade_cost.commission / 2.0
            + trade_cost.slippage / 2.0
            + trade_cost.spread / 2.0
        )
        exit_cost = entry_cost
        events: list[tuple[object, float]] = [(position.start_date, entry_cost)]
        nights = max((position.close_date - position.start_date).days, 0)
        for night in range(1, nights + 1):
            events.append(
                (
                    position.start_date + timedelta(days=night),
                    self.financing_per_lot_per_night * position.lot_size,
                )
            )
        events.append((position.close_date, exit_cost))
        return events
