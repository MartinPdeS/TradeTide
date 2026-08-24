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

### Changed

- Package data and development tooling are configured explicitly.
- Market-loading failures now provide actionable input and dataset errors.
