#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from TradeTide.strategy import MovingAverageCrossing, RelativeStrengthIndex, BollingerBands
from TradeTide.tools import get_dataframe

strategy_list = [
    MovingAverageCrossing,
    RelativeStrengthIndex,
    BollingerBands
]


@pytest.mark.parametrize("strategy", strategy_list, ids=strategy_list)
def test_strategy(strategy):
    dataframe = get_dataframe('eur', 'usd', year=2020)

    sub_frame = dataframe[:10_000].copy()

    strat = RelativeStrengthIndex()

    strat.generate_signal(sub_frame)
