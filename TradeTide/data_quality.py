"""Market-data quality checks that complement native input validation."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from math import isfinite
from typing import TYPE_CHECKING

from TradeTide.debug import logger

if TYPE_CHECKING:
    from TradeTide import Market


class IssueSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class DataQualityIssue:
    severity: IssueSeverity
    code: str
    message: str
    index: int | None = None
    time: datetime | None = None


@dataclass(frozen=True)
class DataQualityReport:
    issues: tuple[DataQualityIssue, ...]

    @property
    def valid(self) -> bool:
        return not any(issue.severity is IssueSeverity.ERROR for issue in self.issues)

    @property
    def errors(self) -> tuple[DataQualityIssue, ...]:
        return tuple(
            issue for issue in self.issues if issue.severity is IssueSeverity.ERROR
        )

    @property
    def warnings(self) -> tuple[DataQualityIssue, ...]:
        return tuple(
            issue for issue in self.issues if issue.severity is IssueSeverity.WARNING
        )

    def raise_for_errors(self) -> None:
        """Raise one actionable error if the report contains invalid data."""
        if self.errors:
            raise ValueError("Market data validation failed: " + self.errors[0].message)


def validate_market_data(
    market: "Market",
    max_spread_ratio: float = 0.01,
) -> DataQualityReport:
    """Check timestamp, OHLC, bid/ask, and spread invariants in a market."""
    if max_spread_ratio <= 0:
        raise ValueError("max_spread_ratio must be positive.")
    issues: list[DataQualityIssue] = []
    dates = list(market.dates)
    expected = len(dates)
    if expected == 0:
        issues.append(
            DataQualityIssue(
                IssueSeverity.ERROR, "empty", "Market has no observations."
            )
        )
        report = DataQualityReport(tuple(issues))
        logger.debug("Market validation: observations=0 errors=1 warnings=0")
        return report
    for side_name, prices in (("ask", market.ask), ("bid", market.bid)):
        for field in ("open", "low", "high", "close"):
            values = list(getattr(prices, field))
            if len(values) != expected:
                issues.append(
                    DataQualityIssue(
                        IssueSeverity.ERROR,
                        "length_mismatch",
                        f"{side_name}.{field} has {len(values)} values; expected {expected}.",
                    )
                )
                continue
            for index, value in enumerate(values):
                if not isfinite(value) or value <= 0:
                    issues.append(
                        DataQualityIssue(
                            IssueSeverity.ERROR,
                            "invalid_price",
                            f"{side_name}.{field} must be finite and positive.",
                            index,
                            dates[index],
                        )
                    )
        for index, (opening, low, high, closing) in enumerate(
            zip(prices.open, prices.low, prices.high, prices.close)
        ):
            if low > min(opening, closing) or high < max(opening, closing):
                issues.append(
                    DataQualityIssue(
                        IssueSeverity.ERROR,
                        "invalid_ohlc",
                        f"{side_name} OHLC range does not contain open and close.",
                        index,
                        dates[index],
                    )
                )
    for index, time in enumerate(dates[1:], start=1):
        if time <= dates[index - 1]:
            issues.append(
                DataQualityIssue(
                    IssueSeverity.ERROR,
                    "timestamp_order",
                    "Timestamps must be strictly increasing with no duplicates.",
                    index,
                    time,
                )
            )
    for index in range(expected):
        if (
            market.bid.low[index] > market.ask.low[index]
            or market.bid.high[index] > market.ask.high[index]
        ):
            issues.append(
                DataQualityIssue(
                    IssueSeverity.ERROR,
                    "crossed_market",
                    "Bid price exceeds ask price.",
                    index,
                    dates[index],
                )
            )
        spread_ratio = (
            market.ask.close[index] - market.bid.close[index]
        ) / market.bid.close[index]
        if spread_ratio > max_spread_ratio:
            issues.append(
                DataQualityIssue(
                    IssueSeverity.WARNING,
                    "wide_spread",
                    f"Spread ratio {spread_ratio:.4%} exceeds {max_spread_ratio:.4%}.",
                    index,
                    dates[index],
                )
            )
    report = DataQualityReport(tuple(issues))
    logger.debug(
        "Market validation: observations=%d errors=%d warnings=%d",
        expected,
        len(report.errors),
        len(report.warnings),
    )
    return report
