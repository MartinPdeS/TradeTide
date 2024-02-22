#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

import pandas
import numpy
from typing import NoReturn
import matplotlib
from TradeTide.strategy.base_strategy import BaseStrategy


class Random(BaseStrategy):
    """
    Implements a Random trading strategy as an extension of the BaseStrategy class.

    This strategy randomly generates a specified number of buy signals (represented as '1') within the trading data.
    It does not follow any financial analysis or market trend and is purely stochastic, serving more as a benchmark or
    for educational purposes rather than a practical trading strategy.

    Attributes:
        number_of_occurence (int): The total number of positive (buy) signals to generate randomly throughout the trading data.

    Methods:
        add_to_ax: Sets the label for the y-axis on a given Matplotlib axis to indicate the use of a random strategy.
        generate_signal: Randomly generates buy signals within the trading data.
    """

    value_type: str = 'close'

    def __init__(self, number_of_occurence: int = 1):
        """
        Initializes a new instance of the Random strategy with a specified number of buy signals to be randomly placed.

        Parameters:
            number_of_occurence (int): The total number of buy signals to be randomly generated. Default is 1.
        """
        self.number_of_occurence = number_of_occurence

    def add_to_ax(self, ax: matplotlib.axes.Axes) -> NoReturn:
        """
        Updates the y-axis label of the given Matplotlib axis to indicate that a random signal strategy is being used.

        This method does not plot any data as the strategy does not produce a continuous metric or indicator.

        Parameters:
            ax (matplotlib.axes.Axes): The Matplotlib axis object to update.
        """
        ax.set_ylabel('Random signal: no metric')

    @BaseStrategy.post_generate_signal
    def generate_signal(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        """
        Generates random buy signals within the given DataFrame based on the specified number of occurrences.

        This method creates a 'signal' column in a new DataFrame, with '1' indicating a buy signal at randomly selected indices,
        and '0' elsewhere.

        Parameters:
            dataframe (pandas.DataFrame): The input DataFrame based on which the length of the trading data is determined.

        Returns:
            pandas.DataFrame: A new DataFrame with the same index as the input DataFrame and a 'signal' column containing randomly
                              placed buy signals.
        """
        random_signal = numpy.zeros(len(dataframe))

        random_index = numpy.random.choice(
            len(dataframe),
            size=self.number_of_occurence,
            replace=True,
            p=None
        )

        random_signal[random_index] = 1

        self.data = pandas.DataFrame(index=dataframe.index)

        self.data['signal'] = random_signal
