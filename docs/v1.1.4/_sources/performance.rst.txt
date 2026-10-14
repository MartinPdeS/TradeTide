Performance and validation
==========================

Every completed :class:`TradeTide.Backtester` returns a structured
``BacktestResult``.  Its ``metrics`` field uses decimal fractions (``0.12`` is
12%) and includes return, annualized return, volatility, maximum drawdown and
its duration, Sharpe, Sortino, and Calmar ratios, win rate, profit factor,
exposure, and trade counts.

Equity and drawdown chart
-------------------------

``BacktestResult.plot_equity_drawdown()`` uses compact green/red equity candles:
each candle opens at the previous observation's equity and closes at the current
one.  The drawdown panel shares its time axis and uses the same net-of-costs
equity curve.

.. code-block:: python

   backtester.run()
   result = BacktestResult.from_portfolio(backtester.portfolio)
   result.plot_equity_drawdown(max_candles=500)

Debug logging
-------------

Logging is opt-in and uses standard Python logging.  DEBUG mode reports market
validation summaries, order lifecycle events, individual trade costs, and final
performance metrics.  ``enable_debug_logging`` also enables native diagnostics
for objects created after it is called.

.. code-block:: python

   import logging
   from TradeTide import configure_logging, enable_debug_logging

   configure_logging(logging.DEBUG)  # Python-side diagnostics
   enable_debug_logging()            # Python and native diagnostics

Execution costs
---------------

Recorded market bid/ask prices already contain their observed spread.  Use
``extra_spread_pips`` only to model additional execution friction.  Commission
and slippage are charged on both entry and exit; financing is charged once per
completed overnight period.  Costs are applied to the returned net equity curve
and trade metrics without changing the raw native record.

.. code-block:: python

   from TradeTide import ExecutionCosts

   costs = ExecutionCosts(
       commission_per_lot=3.50,
       slippage_pips=0.2,
       extra_spread_pips=0.1,
       financing_per_lot_per_night=0.05,
   )
   # Pass execution_costs=costs to Backtester(...).
   backtester.run()
   result = BacktestResult.from_portfolio(backtester.portfolio, costs)
   print(result.metrics.to_dict())

Chronological validation
------------------------

``chronological_split`` never shuffles data, so future observations cannot
leak into training.  ``WalkForwardSplitter`` produces deterministic expanding
or rolling windows and evaluates only the corresponding out-of-sample period.
Supply factories so every fold receives fresh strategy, exit, and sizing state.

.. code-block:: python

   from TradeTide import WalkForwardSplitter

   splitter = WalkForwardSplitter(train_size=2_000, test_size=500, expanding=True)
   report = splitter.run(
       market,
       strategy_factory=lambda training_market: make_strategy(training_market),
       exit_strategy_factory=make_exit_strategy,
       capital_management_factory=make_capital_management,
   )

   for result in report.results:
       print(result.metrics.total_return)
