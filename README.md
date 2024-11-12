# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/MartinPdeS/TradeTide/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                    |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|---------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| TradeTide/backtester.py                 |       35 |        7 |        2 |        1 |     78% |67-86, 149, 169-176 |
| TradeTide/capital\_management.py        |       60 |       24 |       16 |        3 |     54% |49, 101, 104, 115-126, 143, 158-192 |
| TradeTide/indicators/atr.py             |       21 |        9 |        0 |        0 |     57% |42-44, 65-73 |
| TradeTide/indicators/base\_indicator.py |       46 |       19 |        2 |        0 |     56% |25, 35, 38, 46-55, 65, 95-100, 103-114, 137-139, 152 |
| TradeTide/indicators/bb.py              |       28 |        7 |        2 |        0 |     70% |37-42, 54-66 |
| TradeTide/indicators/custom.py          |       16 |        6 |        0 |        0 |     62% |37, 40, 60-66 |
| TradeTide/indicators/mac.py             |       21 |        6 |        0 |        0 |     71% |46-54, 82-92 |
| TradeTide/indicators/macd.py            |       33 |        9 |        2 |        0 |     69% |45-69, 72-77 |
| TradeTide/indicators/random.py          |       20 |        2 |        0 |        0 |     90% |    39, 51 |
| TradeTide/indicators/rmi.py             |       28 |        4 |        0 |        0 |     86% |     46-64 |
| TradeTide/indicators/rsi.py             |       26 |        4 |        0 |        0 |     85% |     43-61 |
| TradeTide/indicators/srsi.py            |       30 |        5 |        0 |        0 |     83% |     43-54 |
| TradeTide/loader.py                     |       40 |        9 |       10 |        4 |     74% |34, 66->69, 70, 89-90, 117-131 |
| TradeTide/metrics.py                    |       66 |        6 |        4 |        2 |     89% |34-38, 62, 155-156 |
| TradeTide/plottings.py                  |       67 |       51 |        8 |        0 |     21% |43-46, 77-115, 133-144, 166-169, 190-203, 218-228, 244-246, 256-280, 291-302, 321-325 |
| TradeTide/position.py                   |      109 |       64 |        8 |        0 |     38% |51, 54-59, 66-72, 82-85, 94, 103, 112, 121-123, 127, 131, 135, 147-150, 157-159, 168-178, 189-192, 201-213, 229, 246-272, 275-279, 286-287, 294-302, 311, 315, 322-323, 332, 339-347, 351 |
| TradeTide/risk\_management.py           |       80 |       47 |       22 |        3 |     35% |32, 75, 90, 94-97, 118, 139-141, 154-164, 182-186, 196-205, 215-218, 231-244 |
| TradeTide/strategy.py                   |       44 |       31 |        8 |        0 |     25% |33-38, 49-59, 62, 65-120 |
| TradeTide/time\_state.py                |       24 |        5 |        0 |        0 |     79% |19-21, 24-25 |
| TradeTide/tools.py                      |       80 |       58 |       36 |        2 |     21% |23-34, 41, 52-65, 72-73, 79-80, 83-90, 93-94, 97-102, 105-117, 120-123 |
|                               **TOTAL** |  **874** |  **373** |  **120** |   **15** | **52%** |           |


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