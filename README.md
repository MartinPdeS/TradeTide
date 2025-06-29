# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/MartinPdeS/TradeTide/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                               |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|--------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| TradeTide/backtester.py                            |        4 |        1 |        0 |        0 |     75% |        13 |
| TradeTide/currencies.py                            |       25 |        1 |        0 |        0 |     96% |        30 |
| TradeTide/data/utils.py                            |       27 |       27 |        8 |        0 |      0% |      1-69 |
| TradeTide/indicators/base.py                       |       20 |       20 |        2 |        0 |      0% |      1-50 |
| TradeTide/indicators/bollinger\_bands.py           |       28 |       28 |        2 |        0 |      0% |     2-103 |
| TradeTide/indicators/moving\_average\_crossings.py |       35 |       35 |        0 |        0 |      0% |     2-103 |
| TradeTide/indicators/relative\_momentum\_index.py  |       39 |       39 |        0 |        0 |      0% |     2-112 |
| TradeTide/loader.py                                |       39 |       32 |       10 |        0 |     14% |26-33, 52-96, 114-128 |
| TradeTide/market.py                                |       91 |       50 |       34 |        3 |     37% |25-46, 116-163, 172-173, 217-218, 225-252 |
| TradeTide/plottings.py                             |       65 |       65 |        8 |        0 |      0% |     4-322 |
| TradeTide/portfolio.py                             |      115 |       32 |       24 |        5 |     69% |64->73, 82, 96, 104, 107, 212-215, 238-239, 262-263, 286-287, 310-315, 327-352 |
| TradeTide/position\_collection.py                  |       34 |       19 |        2 |        0 |     42% |    60-105 |
| TradeTide/signal.py                                |        3 |        0 |        0 |        0 |    100% |           |
| TradeTide/strategy.py                              |        3 |        0 |        0 |        0 |    100% |           |
| TradeTide/times.py                                 |        5 |        0 |        0 |        0 |    100% |           |
| TradeTide/tools.py                                 |       80 |       65 |       36 |        0 |     13% |23-34, 39-65, 72-73, 79-80, 83-90, 93-94, 97-102, 105-117, 120-123 |
|                                          **TOTAL** |  **613** |  **414** |  **126** |    **8** | **29%** |           |


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