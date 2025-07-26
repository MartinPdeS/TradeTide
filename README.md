# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/MartinPdeS/TradeTide/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                               |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|--------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| TradeTide/backtester.py                            |      132 |      116 |       34 |        0 |     10% |18-28, 56-100, 105-136, 140-156, 160-179, 183-209, 213-219, 237-268, 272-316 |
| TradeTide/currencies.py                            |       25 |        0 |        0 |        0 |    100% |           |
| TradeTide/data/utils.py                            |       27 |       27 |        8 |        0 |      0% |      1-69 |
| TradeTide/indicators/base.py                       |       20 |        1 |        2 |        1 |     91% |        47 |
| TradeTide/indicators/bollinger\_bands.py           |       27 |        3 |        2 |        1 |     86% |     72-86 |
| TradeTide/indicators/moving\_average\_crossings.py |       35 |        0 |        0 |        0 |    100% |           |
| TradeTide/indicators/relative\_momentum\_index.py  |       37 |        0 |        0 |        0 |    100% |           |
| TradeTide/loader.py                                |       39 |       32 |       10 |        0 |     14% |26-33, 52-96, 114-128 |
| TradeTide/market.py                                |       92 |       31 |       34 |        9 |     57% |25-46, 118-119, 163-164, 173-174, 218-219, 227-228, 233->239, 239->245, 252-253 |
| TradeTide/plottings.py                             |       65 |       65 |        8 |        0 |      0% |     4-322 |
| TradeTide/portfolio.py                             |      115 |       32 |       24 |        5 |     69% |64->73, 82, 96, 104, 107, 212-215, 238-239, 262-263, 286-287, 310-315, 327-352 |
| TradeTide/position\_collection.py                  |       34 |       19 |        2 |        0 |     42% |    60-105 |
| TradeTide/signal.py                                |        4 |        0 |        0 |        0 |    100% |           |
| TradeTide/simulation\_settings.py                  |       14 |        3 |        4 |        0 |     72% |     16-18 |
| TradeTide/strategy.py                              |        3 |        0 |        0 |        0 |    100% |           |
| TradeTide/times.py                                 |        8 |        0 |        0 |        0 |    100% |           |
| TradeTide/tools.py                                 |       80 |        4 |       36 |        3 |     94% |24-25, 28, 65 |
|                                          **TOTAL** |  **757** |  **333** |  **164** |   **19** | **53%** |           |


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