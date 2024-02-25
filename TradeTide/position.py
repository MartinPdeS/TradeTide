#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from typing import NoReturn
import pandas
import numpy
import matplotlib.pyplot as plt

from dataclasses import dataclass


@dataclass
class Position:
    """
    A class to represent and manage a trading position, including its entry, risk management parameters, and visualization of its lifecycle.

    Attributes:
        start_date (pd.Timestamp): The date when the position is initiated.
        stop_loss (float): The stop-loss threshold, defined as a percentage below the entry price, used to limit potential losses.
        take_profit (float): The take-profit threshold, defined as a percentage above the entry price, used to secure profits.
        market (pd.DataFrame): The market data, which must include a 'close' column that represents the closing prices of the asset.
        units (float): The number of units the position is holding.
        entry_price (float): The price of entry for one unit.

    Methods:
        compute_triggers: Calculates the price levels for stop-loss and take-profit triggers.
        generate_holding_time: Marks the holding period of the position in the market data.
        add_stop_loss_to_ax: Adds stop-loss and take-profit lines to a matplotlib axis.
        add_triggers: Plots the points where stop-loss or take-profit conditions were triggered.
        add_to_ax: Adds the holding period and trigger points to a matplotlib axis for visualization.
        plot: Creates a plot visualizing the position's lifecycle against market data.
    """
    start_date: pandas.Timestamp
    stop_loss: float
    take_profit: float
    market: pandas.DataFrame
    units: float
    entry_price: float

    def __post_init__(self):
        self.start_date = pandas.to_datetime(self.start_date)
        if 'close' not in self.market.columns:
            raise ValueError("Market DataFrame must contain a 'close' column.")

        self.compute_triggers()
        self.compute_exit_price()
        self.entry_value = self.entry_price * self.units
        self.generate_holding_time()

    def compute_exit_price(self):
        """Determines the exit price of the position based on the actual trigger event."""
        self.exit_price = self.market.loc[self.stop_date, 'close'] if self.stop_date else numpy.nan

    def update_cash(self, dataframe: pandas.DataFrame) -> NoReturn:
        entry_spend = self.entry_price * self.units
        exit_get = self.exit_price * self.units

        dataframe.loc[self.start_date:self.stop_date, 'cash'] -= entry_spend
        dataframe.loc[self.stop_date:, 'cash'] += exit_get

    def add_units_to_dataframe(self, dataframe: pandas.DataFrame) -> NoReturn:
        dataframe.loc[self.start_date:self.stop_date, 'units'] += self.units

    def add_holding_to_dataframe(self, dataframe: pandas.DataFrame) -> NoReturn:
        dataframe.loc[self.start_date:self.stop_date, 'positions'] += 1

    def add_holding_value_to_dataframe(self, dataframe: pandas.DataFrame) -> NoReturn:
        dataframe.loc[self.start_date:self.stop_date, 'holdings_value'] += self.units * self.market.close

    def compute_triggers(self) -> NoReturn:
        """Computes and sets the trigger levels and dates for stop-loss and take-profit conditions."""
        self.stop_loss_price = self.entry_price * (1 - self.stop_loss)
        self.take_profit_price = self.entry_price * (1 + self.take_profit)

        market_after_start = self.market.loc[self.start_date:]

        self.take_profit_trigger = market_after_start[market_after_start['close'] >= self.take_profit_price].first_valid_index()
        self.stop_loss_trigger = market_after_start[market_after_start['close'] <= self.stop_loss_price].first_valid_index()

        self.stop_date = min(filter(pandas.notna, [self.take_profit_trigger, self.stop_loss_trigger, self.market.index[-1]]))

    def generate_holding_time(self):
        """Marks the holding period of the position within the market data timeframe."""
        self.holding = pandas.Series(0, index=self.market.index)
        self.holding.loc[self.start_date:self.stop_date] = 1

    def add_stop_loss_to_ax(self, ax: plt.Axes) -> NoReturn:
        ax.hlines(
            y=self.stop_loss_price,
            color='red',
            linestyle='--',
            linewidth=1,
            label='Stop-loss',
            xmin=self.start_date,
            xmax=self.stop_date
        )

        ax.hlines(
            y=self.take_profit_price,
            color='green',
            linestyle='--',
            linewidth=1,
            label='Take-profit',
            xmin=self.start_date,
            xmax=self.stop_date
        )

    def add_triggers(self, ax: plt.Axes) -> NoReturn:
        if self.take_profit_trigger:
            ax.scatter(
                x=self.take_profit_trigger,
                y=self.market.at[self.take_profit_trigger, 'close'],
                color='green',
                label='Take-profit Triggered',
                zorder=5
            )

        if self.stop_loss_trigger:
            ax.scatter(
                x=self.stop_loss_trigger,
                y=self.market.at[self.stop_loss_trigger, 'close'],
                color='red',
                label='Stop-loss Triggered',
                zorder=5
            )

    def add_holding_area_to_ax(self, ax: plt.Axes) -> NoReturn:
        """Adds visual elements like stop-loss and take-profit lines to the given Matplotlib axis."""
        ax.fill_between(
            self.market.index,
            y1=0,
            y2=1,
            where=self.holding != 0,
            transform=ax.get_xaxis_transform(),
            color='gray',
            alpha=0.3,
            label='Holding Period'
        )

    def plot(self) -> NoReturn:
        """Plots the position's market data, highlighting the holding period, stop-loss, and take-profit levels."""
        ax = self.market['close'].plot(
            figsize=(10, 6),
            title='Position Overview',
            label='Market Close'
        )

        self.add_holding_area_to_ax(ax=ax)
        self.add_triggers(ax=ax)
        self.add_stop_loss_to_ax(ax=ax)
        plt.legend()
        plt.show()
