"""
Market Data Quality Checks
==========================

Validate a market after loading it and before research or backtesting.  The
report distinguishes invalid data (errors) from suspicious-but-usable data
(warnings), such as unusually wide bid/ask spreads.
"""

# %%
# This example deliberately uses a wide, but valid, spread to demonstrate a
# warning.  Native market construction still guards basic bid/ask and OHLC
# invariants at insertion time.

from datetime import datetime

from TradeTide import Market, validate_market_data

market = Market()
market.add_market_data(
    datetime(2024, 1, 1, 9),
    1.2000,  # ask open
    1.2100,  # ask high
    1.1900,  # ask low
    1.2000,  # ask close
    1.0000,  # bid open
    1.0100,  # bid high
    0.9900,  # bid low
    1.0000,  # bid close
)

report = validate_market_data(market, max_spread_ratio=0.01)
print(f"valid: {report.valid}")
for issue in report.issues:
    print(f"{issue.severity.value}: {issue.code} — {issue.message}")

# %%
# Use ``raise_for_errors`` when a pipeline should stop on invalid data.  Warnings
# remain visible but do not prevent a backtest.

report.raise_for_errors()
