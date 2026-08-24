# Changelog

All notable changes to TradeTide are documented here.

## Unreleased

### Added

- Relative Strength Index (RSI) and MACD indicators.
- Composable `all_of`, `any_of`, and weighted signal rules.
- Validation tests for market loading and signal composition.
- Structured backtest results, all-in execution-cost reporting, and chronological
  train/test and walk-forward validation utilities.
- Native-binding smoke tests, package typing metadata, and a Python 3.10–3.13
  quality workflow for pull requests and pushes.
- Batched, automatically decimated candlestick charts for efficient market
  visualisation across all market plots.
- Deterministic OHLC market, limit, stop, and stop-limit order triggering;
  trade ledgers with MAE/MFE analytics; and market-data quality reports.
- Calmar ratio, maximum drawdown duration, equity-candle/drawdown plots, opt-in
  structured debug logging, and an end-to-end strategy tutorial.

### Changed

- Package data and development tooling are configured explicitly.
- Market-loading failures now provide actionable input and dataset errors.
