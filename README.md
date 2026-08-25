# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/MartinPdeS/TradeTide/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                              |    Stmts |     Miss |   Branch |   BrPart |      Cover |   Missing |
|---------------------------------- | -------: | -------: | -------: | -------: | ---------: | --------: |
| TradeTide/currencies.py           |       25 |        1 |        0 |        0 |     96.00% |        31 |
| TradeTide/data/utils.py           |       25 |       25 |        8 |        0 |      0.00% |      1-69 |
| TradeTide/data\_quality.py        |       62 |        9 |       30 |        6 |     83.70% |51-\>exit, 61, 66-73, 78-85, 88, 126 |
| TradeTide/debug.py                |       21 |       14 |        2 |        0 |     30.43% |12-25, 30-33, 38-41 |
| TradeTide/performance.py          |      248 |       90 |       66 |       15 |     59.55% |95, 196, 203-216, 221, 224-226, 237, 239-\>235, 317, 329, 332, 338-339, 367-533, 550, 559, 563-565, 570-573, 624 |
| TradeTide/simulation\_settings.py |       14 |       14 |        4 |        0 |      0.00% |      4-22 |
| TradeTide/tools.py                |       80 |       65 |       36 |        0 |     12.93% |23-34, 39-69, 74-75, 80-81, 84-91, 94-95, 98-103, 106-118, 121-124 |
| TradeTide/utils.py                |        2 |        2 |        0 |        0 |      0.00% |       4-7 |
| TradeTide/validation.py           |       57 |       16 |       18 |        6 |     68.00% |46, 49, 62, 97, 103, 121, 140-156 |
| **TOTAL**                         |  **572** |  **236** |  **172** |   **27** | **54.70%** |           |

2 files skipped due to complete coverage.


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