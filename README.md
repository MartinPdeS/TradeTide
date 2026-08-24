# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/MartinPdeS/TradeTide/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                              |    Stmts |     Miss |   Branch |   BrPart |      Cover |   Missing |
|-------------------------------------------------- | -------: | -------: | -------: | -------: | ---------: | --------: |
| TradeTide/backtester.py                           |      104 |       79 |       20 |        0 |     20.16% |42-55, 65-80, 98-123, 129-173, 178-221, 226-264, 269-306, 311-331 |
| TradeTide/currencies.py                           |       25 |        1 |        0 |        0 |     96.00% |        31 |
| TradeTide/data/utils.py                           |       25 |       25 |        8 |        0 |      0.00% |      1-69 |
| TradeTide/data\_quality.py                        |       62 |        9 |       30 |        6 |     83.70% |51-\>exit, 61, 66-73, 78-85, 88, 126 |
| TradeTide/debug.py                                |       21 |       14 |        2 |        0 |     30.43% |12-25, 30-33, 38-41 |
| TradeTide/indicators/bollinger\_bands.py          |       28 |        3 |        2 |        1 |     86.67% |     61-75 |
| TradeTide/indicators/macd.py                      |       20 |        8 |        4 |        0 |     50.00% |     24-34 |
| TradeTide/indicators/relative\_strength\_index.py |       17 |        6 |        4 |        0 |     52.38% |     20-25 |
| TradeTide/ledger.py                               |       33 |        3 |        2 |        0 |     91.43% | 85, 89-91 |
| TradeTide/market\_plotting.py                     |       43 |        2 |       10 |        2 |     92.45% |    43, 46 |
| TradeTide/orders.py                               |       99 |       12 |       40 |       12 |     82.73% |51, 53, 57, 62, 64, 95, 110-\>113, 114, 123-125, 127-\>119, 177, 185 |
| TradeTide/performance.py                          |      188 |       34 |       52 |       15 |     76.25% |93, 182-195, 200, 203-205, 216, 218-\>214, 296, 308, 311, 317-318, 352, 361, 365-367, 372-375, 426 |
| TradeTide/plotting.py                             |       34 |        9 |       10 |        2 |     65.91% |25-\>27, 28, 41-48 |
| TradeTide/portfolio.py                            |      100 |       30 |       16 |        1 |     68.10% |55-\>exit, 184-193, 205-208, 220-221, 233-239, 252-257, 268-303 |
| TradeTide/position\_collection.py                 |       32 |       17 |        2 |        0 |     44.12% |     47-88 |
| TradeTide/simulation\_settings.py                 |       14 |        3 |        4 |        0 |     72.22% |     17-19 |
| TradeTide/tools.py                                |       80 |       65 |       36 |        0 |     12.93% |23-34, 39-69, 74-75, 80-81, 84-91, 94-95, 98-103, 106-118, 121-124 |
| TradeTide/validation.py                           |       57 |       16 |       18 |        6 |     68.00% |46, 49, 62, 97, 103, 121, 140-156 |
| **TOTAL**                                         | **1154** |  **336** |  **274** |   **45** | **66.46%** |           |

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