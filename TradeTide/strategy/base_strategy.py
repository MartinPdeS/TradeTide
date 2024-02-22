#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

import pandas
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt


class BaseStrategy(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def generate_signal(self) -> pandas.DataFrame:
        pass

    def plot(self):
        figure, ax = plt.subplots(1, 1, figsize=(12, 4))
        self.add_to_ax(ax)

        plt.show()

    @property
    def signal(self) -> pandas.Series:
        return self.data['signal']

    def add_to_ax(self, ax):
        pass

    def post_generate_signal(function):
        def wrapper(self, dataframe):
            self.data = pandas.DataFrame(index=dataframe.index)
            self.data[self.value_type] = dataframe[self.value_type]

            function(self, dataframe=dataframe)

            return self.data['signal']

        return wrapper
