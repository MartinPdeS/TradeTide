# Changelog

All notable changes to TradeTide are documented here.

## Unreleased

### Added

- Local browser GUI launched with `TradeTide`, `tradetide-gui`, or
  `python -m TradeTide.gui`, with a research library and separate strategy,
  results, orders/trades, and comparison tabs.
- Configurable stacks of up to eight indicators, signal voting, exit policies,
  position sizing, and execution costs; parameter sweeps validate two to six
  candidates before running and allow stopping the remaining queue.
- Autosaved drafts, up to 20 named strategies, and browser persistence for the
  last 30 runs, with reversible settings imports and portable JSON exports.
- Side-by-side run comparisons with normalized equity overlays for matching
  samples and a table of changed parameters.
- Interactive chart ranges and keyboard inspection, indicator diagnostics,
  executed/skipped entry requests, sortable trade filters, trade details with
  chart navigation, and filtered CSV exports.
- GUI backend, research-helper, and browser regression checks covering native
  backtests, persistence, sweeps, queue cancellation, and responsive layouts.
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

- Moved C++ sources from `TradeTide/cpp/` to root-level `cpp/` and updated CMake
  and source-distribution configuration; extensions still install directly
  into the `TradeTide` package.
- Moved the Conda recipe to `conda.recipe/meta.yaml` and updated its source path,
  native-library paths, launcher smoke check, and release workflow reference.
- Package data and development tooling are configured explicitly.
- Market-loading failures now provide actionable input and dataset errors.

### Removed

- Unused `TradeTide.binary` compatibility package and its obsolete build,
  cleanup, and typing references.
