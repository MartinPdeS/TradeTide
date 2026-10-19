:orphan:

.. _theory:

How it works
============

TradeTide turns market data into reproducible backtests through a small set of
cooperating components:

* **Market data** provides timestamped prices and normalizes them into the
  common series used by the rest of the package.
* **Signal rules** convert prices and indicators into entry and exit signals.
* **The backtester** applies those signals, manages positions and cash, and
  records every transaction in a structured result.
* **Costs and execution** model spreads, commissions, slippage, and position
  sizing so the simulated fills remain explicit.
* **Performance analysis** turns the trade ledger and equity curve into return,
  risk, drawdown, and ratio metrics.
* **The graphical workspace** exposes the same workflow interactively for
  exploring data, strategies, and saved configurations.

The sections below describe the models and conventions used by each component.
