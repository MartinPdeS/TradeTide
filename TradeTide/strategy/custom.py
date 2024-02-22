#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

import pandas
import numpy
from TradeTide.strategy.base_strategy import BaseStrategy


class Custom(BaseStrategy):
    def __init__(self, custom_signal: numpy.ndarray):
        self.custom_signal = custom_signal

    @BaseStrategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        assert len(dataframe) == len(self.custom_signal), 'Mismatch between the custom signal and dataframe'

        self.data['signal'] = self.custom_signal
