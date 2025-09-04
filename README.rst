|logo|

.. list-table::
   :widths: 10 25 25 25
   :header-rows: 0

   * - Meta
     - |python|
     - |docs|
     -
   * - Testing
     - |ci/cd|
     - |coverage|
     - |colab|
   * - PyPI
     - |PyPI|
     - |PyPI_download|
     -
   * - Anaconda
     - |anaconda|
     - |anaconda_download|
     - |anaconda_date|

TradeTide
=========

TradeTide is a trading platform designed to empower traders with advanced analytics, real-time market data, and automated trading capabilities. Our platform caters to both novice and experienced traders, offering a wide range of tools to analyze market trends, execute trades, and manage portfolios efficiently.


Testing
*******

To test localy (with cloning the GitHub repository) you'll need to install the dependencies and run the coverage command as

.. code:: python

   >>> git clone https://github.com/MartinPdeS/TradeTide.git
   >>> cd TradeTide
   >>> pip install -r requirements/requirements.txt
   >>> pytest

----


Coding example
**************

.. code-block:: python

   from TradeTide import Backtester, Strategy, Market, Currency, days, hours, minutes
   from TradeTide.indicators import BollingerBands
   from TradeTide import capital_management, exit_strategy

   market = Market()

   market.load_from_database(
      currency_0=Currency.CAD,
      currency_1=Currency.USD,
      time_span=100 * days,
   )

   indicator = BollingerBands(
      window=3 * minutes,
      multiplier=2.0
   )

   indicator.run(market)

   strategy = Strategy()

   strategy.add_indicator(indicator)

   exit_strategy = exit_strategy.Static(
      stop_loss=4,
      take_profit=4,
      save_price_data=True
   )

   capital_management = capital_management.FixedLot(
      capital=1_000_000,
      fixed_lot_size=10_000,
      max_capital_at_risk=100_000,
      max_concurrent_positions=100,
   )

   backtester = Backtester(
      strategy=strategy,
      exit_strategy=exit_strategy,
      market=market,
      capital_management=capital_management,
   )

   backtester.run()

   backtester.print_performance()


|example|

----


Contact Information
************************
As of 2025, the project is still under development. If you want to collaborate, it would be a pleasure! I encourage you to contact me.

TradeTide was written by `Martin Poinsinet de Sivry-Houle <https://github.com/MartinPdS>`_  .

Email:`martin.poinsinet-de-sivry@polymtl.ca <mailto:martin.poinsinet.de.sivry@gmail.com?subject=TradeTide>`_ .

.. |logo| image:: https://github.com/MartinPdeS/TradeTide/raw/master/docs/images/logo.png
    :alt: TradeTide logo
.. |python| image:: https://img.shields.io/pypi/pyversions/tradetide.svg
    :alt: Python
    :target: https://www.python.org/
.. |colab| image:: https://colab.research.google.com/assets/colab-badge.svg
    :alt: Google Colab
    :target: https://colab.research.google.com/github/MartinPdeS/TradeTide/blob/master/notebook.ipynb
.. |docs| image:: https://github.com/martinpdes/tradetide/actions/workflows/deploy_documentation.yml/badge.svg
    :target: https://martinpdes.github.io/TradeTide/
    :alt: Documentation Status
.. |PyPI| image:: https://badge.fury.io/py/TradeTide.svg
    :alt: PyPI version
    :target: https://badge.fury.io/py/TradeTide
.. |PyPI_download| image:: https://img.shields.io/pypi/dm/TradeTide?style=plastic&label=PyPI%20downloads&labelColor=hex&color=hex
    :alt: PyPI downloads
    :target: https://pypistats.org/packages/tradetide
.. |coverage| image:: https://raw.githubusercontent.com/MartinPdeS/TradeTide/python-coverage-comment-action-data/badge.svg
    :alt: Unittest coverage
    :target: https://htmlpreview.github.io/?https://github.com/MartinPdeS/TradeTide/blob/python-coverage-comment-action-data/htmlcov/index.html
.. |ci/cd| image:: https://github.com/martinpdes/tradetide/actions/workflows/deploy_coverage.yml/badge.svg
    :alt: Unittest Status
.. |example| image:: https://github.com/MartinPdeS/TradeTide/raw/master/docs/images/image_example.png
    :width: 800
    :alt: Qsca vs diameter
.. |anaconda| image:: https://anaconda.org/martinpdes/tradetide/badges/version.svg
    :alt: Anaconda version
    :target: https://anaconda.org/martinpdes/tradetide
.. |anaconda_download| image:: https://anaconda.org/martinpdes/tradetide/badges/downloads.svg
    :alt: Anaconda downloads
    :target: https://anaconda.org/martinpdes/tradetide
.. |anaconda_date| image:: https://anaconda.org/martinpdes/tradetide/badges/latest_release_relative_date.svg
    :alt: Latest release date
    :target: https://anaconda.org/martinpdes/tradetide
