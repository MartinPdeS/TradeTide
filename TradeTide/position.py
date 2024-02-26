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
    Manages a trading position with entry, risk management, and visualization.

    Attributes:
        start_date (pd.Timestamp): Date when the position is opened.
        stop_loss (float): Percentage below the entry price for the stop-loss level.
        take_profit (float): Percentage above the entry price for the take-profit level.
        market (pd.DataFrame): Market data with at least 'close' prices.
        units (float): Number of units involved in the position.
        entry_price (float): Price at which the position is entered.
        type (str): Type of position, either short or long

    Methods:
        compute_exit_price: Determines the exit price based on the trigger events.
        update_cash: Updates the cash balance based on position entry and exit.
        add_units_to_dataframe: Adds the position's units to a DataFrame during the holding period.
        compute_triggers: Identifies the trigger levels and dates for stop-loss and take-profit.
        generate_holding_time: Marks the holding period within the market data timeframe.
        plot: Visualizes the position lifecycle against the market data.
    """
    start_date: pandas.Timestamp
    stop_loss: float
    take_profit: float
    market: pandas.DataFrame
    units: float
    entry_price: float
    type: str

    def __post_init__(self):
        self.start_date = pandas.to_datetime(self.start_date)

        self.validate_market_data()
        self.compute_triggers()
        self.compute_exit_price()
        self.entry_value = self.entry_price * self.units
        self.generate_holding_time()

    def validate_market_data(self):
        """Ensures the market data contains the required 'close' column."""
        if 'close' not in self.market.columns:
            raise ValueError("The market DataFrame must contain a 'close' column.")

    def compute_exit_price(self):
        """Determines the exit price of the position based on the actual trigger event."""
        self.exit_price = self.market.loc[self.stop_date, 'close'] if self.stop_date else numpy.nan

    def update_cash(self, dataframe: pandas.DataFrame) -> NoReturn:
        entry_spend = self.entry_price * self.units
        exit_get = self.exit_price * self.units

        dataframe.loc[self.start_date:self.stop_date, 'cash'] -= entry_spend
        dataframe.loc[self.stop_date:, 'cash'] += exit_get

    def update_portfolio_dataframe(self, dataframe: pandas.DataFrame) -> NoReturn:
        self.add_units_to_dataframe(dataframe=dataframe)
        self.add_holding_value_to_dataframe(dataframe=dataframe)
        self.add_position_to_dataframe(dataframe=dataframe)
        self.update_cash(dataframe=dataframe)

    def add_units_to_dataframe(self, dataframe: pandas.DataFrame) -> NoReturn:
        dataframe.loc[self.start_date:self.stop_date, 'units'] += self.units

    def add_position_to_dataframe(self, dataframe: pandas.DataFrame) -> NoReturn:
        if self.type == 'short':
            dataframe.loc[self.start_date:self.stop_date, 'short_positions'] += 1
        else:
            dataframe.loc[self.start_date:self.stop_date, 'long_positions'] += 1

    def add_holding_value_to_dataframe(self, dataframe: pandas.DataFrame) -> NoReturn:
        dataframe.loc[self.start_date:self.stop_date, 'holdings'] += self.units * self.market.close

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
                s=10,
                label='Take-profit Triggered',
                zorder=5
            )

        if self.stop_loss_trigger:
            ax.scatter(
                x=self.stop_loss_trigger,
                y=self.market.at[self.stop_loss_trigger, 'close'],
                color='red',
                s=10,
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
