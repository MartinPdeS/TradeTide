# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/MartinPdeS/TradeTide/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                              |    Stmts |     Miss |   Branch |   BrPart |      Cover |   Missing |
|-------------------------------------------------- | -------: | -------: | -------: | -------: | ---------: | --------: |
| TradeTide/backtester.py                           |      100 |       76 |       20 |        0 |     20.00% |40-53, 63-67, 85-110, 116-155, 160-203, 208-246, 251-288, 293-313 |
| TradeTide/currencies.py                           |       25 |        1 |        0 |        0 |     96.00% |        31 |
| TradeTide/data/utils.py                           |       25 |       25 |        8 |        0 |      0.00% |      1-69 |
| TradeTide/indicators/bollinger\_bands.py          |       27 |        3 |        2 |        1 |     86.21% |     61-75 |
| TradeTide/indicators/macd.py                      |       20 |        8 |        4 |        0 |     50.00% |     24-34 |
| TradeTide/indicators/relative\_strength\_index.py |       17 |        6 |        4 |        0 |     52.38% |     20-25 |
| TradeTide/market.py                               |      126 |        4 |       36 |        3 |     94.44% |59-60, 185, 241 |
| TradeTide/performance.py                          |      123 |        7 |       22 |        7 |     88.97% |87, 150, 152-\>148, 224, 236, 239, 245-246 |
| TradeTide/plotting.py                             |       34 |        9 |       10 |        2 |     65.91% |25-\>27, 28, 41-48 |
| TradeTide/portfolio.py                            |       98 |       30 |       16 |        1 |     67.54% |55-\>exit, 176-185, 197-200, 212-213, 225-231, 244-249, 260-295 |
| TradeTide/position\_collection.py                 |       31 |       16 |        2 |        0 |     45.45% |     48-88 |
| TradeTide/simulation\_settings.py                 |       14 |        3 |        4 |        0 |     72.22% |     17-19 |
| TradeTide/tools.py                                |       80 |       65 |       36 |        0 |     12.93% |23-34, 39-69, 74-75, 80-81, 84-91, 94-95, 98-103, 106-118, 121-124 |
| TradeTide/validation.py                           |       67 |       16 |       18 |        6 |     71.76% |48, 51, 64, 99, 105, 123, 142-158 |
| **TOTAL**                                         |  **958** |  **269** |  **196** |   **20** | **66.98%** |           |

9 files skipped due to complete coverage.


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