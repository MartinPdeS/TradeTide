# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/MartinPdeS/TradeTide/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                     |    Stmts |     Miss |   Branch |   BrPart |      Cover |   Missing |
|----------------------------------------- | -------: | -------: | -------: | -------: | ---------: | --------: |
| TradeTide/backtester.py                  |       92 |       71 |       20 |        0 |     18.75% |33-44, 63-88, 94-133, 138-181, 186-224, 229-266, 271-291 |
| TradeTide/currencies.py                  |       25 |        1 |        0 |        0 |     96.00% |        31 |
| TradeTide/data/utils.py                  |       27 |       27 |        8 |        0 |      0.00% |      1-73 |
| TradeTide/indicators/bollinger\_bands.py |       27 |        3 |        2 |        1 |     86.21% |     61-75 |
| TradeTide/market.py                      |       75 |       25 |       18 |        1 |     56.99% |26-52, 221-228 |
| TradeTide/portfolio.py                   |       97 |       28 |       16 |        1 |     69.03% |56->exit, 177-186, 198-201, 213-214, 226-232, 245-250, 261-294 |
| TradeTide/position\_collection.py        |       31 |       16 |        2 |        0 |     45.45% |     48-88 |
| TradeTide/simulation\_settings.py        |       14 |        3 |        4 |        0 |     72.22% |     17-19 |
| TradeTide/tools.py                       |       80 |       65 |       36 |        0 |     12.93% |23-34, 39-69, 74-75, 80-81, 84-91, 94-95, 98-103, 106-118, 121-124 |
|                                **TOTAL** |  **574** |  **239** |  **108** |    **3** | **51.61%** |           |

7 files skipped due to complete coverage.


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