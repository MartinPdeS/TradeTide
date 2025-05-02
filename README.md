# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/MartinPdeS/TradeTide/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                    |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|---------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| TradeTide/backtester.py                 |       35 |        7 |        2 |        1 |     78% |67-86, 149, 169-176 |
| TradeTide/capital\_management.py        |       59 |       24 |       16 |        3 |     53% |47, 99, 102, 113-124, 141, 156-190 |
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
| TradeTide/loader.py                     |       39 |        9 |       10 |        4 |     73% |31, 63->66, 67, 86-87, 114-128 |
| TradeTide/metrics.py                    |       65 |        6 |        4 |        2 |     88% |31-35, 59, 152-153 |
| TradeTide/plottings.py                  |       65 |       51 |        8 |        0 |     19% |40-43, 74-112, 130-141, 163-166, 187-200, 215-225, 241-243, 253-277, 288-299, 318-322 |
| TradeTide/position.py                   |      106 |       64 |        8 |        0 |     37% |48, 51-56, 63-69, 79-82, 91, 100, 109, 118-120, 124, 128, 132, 144-147, 154-156, 165-175, 186-189, 198-210, 226, 243-269, 272-276, 283-284, 291-299, 308, 312, 319-320, 329, 336-344, 348 |
| TradeTide/position\_collection.py       |       18 |       18 |        2 |        0 |      0% |      1-36 |
| TradeTide/risk\_management.py           |       80 |       47 |       22 |        3 |     35% |32, 75, 90, 94-97, 118, 139-141, 154-164, 182-186, 196-205, 215-218, 231-244 |
| TradeTide/strategy.py                   |       43 |       31 |        8 |        0 |     24% |31-36, 47-57, 60, 63-118 |
| TradeTide/time\_state.py                |       23 |        5 |        0 |        0 |     78% |16-18, 21-22 |
| TradeTide/tools.py                      |       80 |       58 |       36 |        2 |     21% |23-34, 41, 52-65, 72-73, 79-80, 83-90, 93-94, 97-102, 105-117, 120-123 |
|                               **TOTAL** |  **882** |  **391** |  **122** |   **15** | **51%** |           |


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