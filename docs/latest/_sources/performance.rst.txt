Performance and validation
==========================

Every completed :class:`TradeTide.Backtester` returns a structured
``BacktestResult``.  Its ``metrics`` field uses decimal fractions (``0.12`` is
12%) and includes return, annualized return, volatility, maximum drawdown,
Sharpe and Sortino ratios, win rate, profit factor, exposure, and trade counts.

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
   result = backtester.run()
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
