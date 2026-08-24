|logo|

.. list-table::
   :widths: 35 65
   :header-rows: 1

   * - Badge
     - Status
   * - Python versions
     - |python|
   * - Documentation
     - |docs|
   * - Continuous integration
     - |ci/cd|
   * - Test coverage
     - |coverage|
   * - Google Colab
     - |colab|
   * - PyPI package
     - |PyPI|
   * - PyPI downloads
     - |PyPI_download|
   * - Anaconda package
     - |anaconda|
   * - Anaconda downloads
     - |anaconda_download|
   * - Latest Anaconda release
     - |anaconda_date|

TradeTide
=========

**TradeTide** is a Python/C++ package for researching and backtesting
foreign-exchange trading strategies. It includes bundled historical samples,
technical indicators, position management, and portfolio simulation.

Features
--------

- Bundled historical samples for five major FX pairs.
- Technical indicators including Bollinger Bands, moving-average crossings,
  RMI, RSI, and MACD.
- Composable ``all_of``, ``any_of``, and weighted signal rules.
- Backtesting with configurable exit and capital-management strategies.

Installation
------------

TradeTide is available from PyPI and Anaconda:

.. code-block:: console

   pip install TradeTide
   conda install TradeTide --channel MartinPdeS

Verify the installation with the Python interpreter used for backtests:

.. code-block:: console

   python -c "import TradeTide; print(TradeTide.__version__)"

Released wheels are the easiest option. Building from source requires CMake,
a C++20 compiler, pybind11, and OpenMP.

First backtest
--------------

Load the bundled EUR/USD sample, add an indicator to a strategy, and run a
backtest:

.. code-block:: python

   from TradeTide import Backtester, Currency, Market, Strategy
   from TradeTide import capital_management, exit_strategy
   from TradeTide.indicators import BollingerBands
   from TradeTide.times import days, minutes

   market = Market()
   market.load_from_database(Currency.EUR, Currency.USD, time_span=3 * days)

   strategy = Strategy()
   strategy.add_indicator(BollingerBands(window=30 * minutes, multiplier=2.0))

   backtester = Backtester(
       strategy=strategy,
       market=market,
       exit_strategy=exit_strategy.Static(stop_loss=4, take_profit=4),
       capital_management=capital_management.FixedLot(
           capital=100_000,
           fixed_lot_size=10_000,
           max_capital_at_risk=10_000,
           max_concurrent_positions=1,
       ),
   )
   backtester.run()
   backtester.plot()

Bundled datasets are EUR/USD, GBP/USD, CHF/USD, JPY/USD, and CAD/USD.
``time_span`` accepts a ``timedelta`` or a positive duration string such as
``"2d 6h"``.

Testing
-------

For local development, install the development extra and run the suite:

.. code-block:: console

   git clone https://github.com/MartinPdeS/TradeTide.git
   cd TradeTide
   pip install -e '.[dev]'
   pytest

Contributing
------------

See `CONTRIBUTING.md <CONTRIBUTING.md>`_ for the native-build requirements,
formatting checks, and pull-request guidelines.

Contact
-------

For questions or contributions, contact
`martin.poinsinet.de.sivry@gmail.com <mailto:martin.poinsinet.de.sivry@gmail.com>`_.

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
.. |anaconda| image:: https://anaconda.org/martinpdes/tradetide/badges/version.svg
    :alt: Anaconda version
    :target: https://anaconda.org/martinpdes/tradetide
.. |anaconda_download| image:: https://anaconda.org/martinpdes/tradetide/badges/downloads.svg
    :alt: Anaconda downloads
    :target: https://anaconda.org/martinpdes/tradetide
.. |anaconda_date| image:: https://anaconda.org/martinpdes/tradetide/badges/latest_release_relative_date.svg
    :alt: Latest release date
    :target: https://anaconda.org/martinpdes/tradetide
