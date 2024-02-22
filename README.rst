|Logo|

|python|


TradeTide
=========

TradeTide is a trading platform designed to empower traders with advanced analytics, real-time market data, and automated trading capabilities. Our platform caters to both novice and experienced traders, offering a wide range of tools to analyze market trends, execute trades, and manage portfolios efficiently.


Testing
*******

To test localy (with cloning the GitHub repository) you'll need to install the dependencies and run the coverage command as

.. code:: python

   >>> git clone https://github.com/MartinPdeS/PyMieSim.git
   >>> cd PyMieSim
   >>> pip install -r requirements/requirements.txt
   >>> pytest

----


Coding example
**************

.. code-block:: python

   >>> from TradeTide import BackTester, RelativeStrengthIndex, get_market_data
   >>>
   >>> market_data = get_market_data('eur', 'usd', year=2023)
   >>>
   >>> strategy = RelativeStrengthIndex(period='30min', overbought_threshold=90, oversold_threshold=10)
   >>>
   >>> strategy.generate_signal(market_data)
   >>>
   >>> backtester = BackTester(market=market_data, strategy=strategy)
   >>>
   >>> backtester.back_test(stop_loss='.1%', take_profit='.1%', spread=0)
   >>>
   >>> portfolio = backtester.portfolio
   >>>
   >>> backtester.plot()
   >>>
   >>> backtester.calculate_performance_metrics()
   >>>
   >>> final_portfolio_value = backtester.get_final_portfolio_value()
   >>>
   >>> print(f"Final Portfolio Value: {final_portfolio_value}")



----


Contact Information
************************
As of 2023, the project is still under development. If you want to collaborate, it would be a pleasure! I encourage you to contact me.

PyMieSim was written by `Martin Poinsinet de Sivry-Houle <https://github.com/MartinPdS>`_  .

Email:`martin.poinsinet-de-sivry@polymtl.ca <mailto:martin.poinsinet-de-sivry@polymtl.ca?subject=TradeTide>`_ .


.. |python| image:: https://img.shields.io/pypi/pyversions/pymiesim.svg
   :target: https://www.python.org/

.. |Logo| image:: https://github.com/MartinPdeS/TradeTide/raw/master/docs/images/logo.png