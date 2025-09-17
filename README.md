# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/MartinPdeS/TradeTide/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                               |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|--------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| TradeTide/backtester.py                            |      153 |      127 |       24 |        0 |     15% |33-44, 62-83, 89-128, 133-176, 181-219, 224-261, 266-286, 298-327, 332-387, 397-440 |
| TradeTide/currencies.py                            |       25 |        0 |        0 |        0 |    100% |           |
| TradeTide/data/utils.py                            |       27 |       27 |        8 |        0 |      0% |      1-73 |
| TradeTide/indicators/base.py                       |       24 |        0 |        2 |        0 |    100% |           |
| TradeTide/indicators/bollinger\_bands.py           |       29 |        3 |        2 |        1 |     87% |     61-75 |
| TradeTide/indicators/moving\_average\_crossings.py |       35 |        0 |        0 |        0 |    100% |           |
| TradeTide/indicators/relative\_momentum\_index.py  |       34 |        0 |        0 |        0 |    100% |           |
| TradeTide/loader.py                                |       39 |       32 |       10 |        0 |     14% |27-34, 59-103, 121-129 |
| TradeTide/market.py                                |       75 |       25 |       18 |        1 |     57% |26-52, 221-228 |
| TradeTide/portfolio.py                             |       97 |       28 |       16 |        1 |     69% |56->exit, 177-186, 198-201, 213-214, 226-232, 245-250, 261-294 |
| TradeTide/position\_collection.py                  |       31 |       16 |        2 |        0 |     45% |     48-88 |
| TradeTide/signal.py                                |        4 |        0 |        0 |        0 |    100% |           |
| TradeTide/simulation\_settings.py                  |       14 |        3 |        4 |        0 |     72% |     17-19 |
| TradeTide/strategy.py                              |        3 |        0 |        0 |        0 |    100% |           |
| TradeTide/times.py                                 |        8 |        0 |        0 |        0 |    100% |           |
| TradeTide/tools.py                                 |       80 |        4 |       36 |        3 |     94% |24-25, 28, 69 |
| TradeTide/utils.py                                 |        2 |        0 |        0 |        0 |    100% |           |
|                                          **TOTAL** |  **680** |  **265** |  **122** |    **6** | **58%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/MartinPdeS/TradeTide/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/MartinPdeS/TradeTide/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/MartinPdeS/TradeTide/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/MartinPdeS/TradeTide/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2FMartinPdeS%2FTradeTide%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/MartinPdeS/TradeTide/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.