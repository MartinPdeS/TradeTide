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
    Represents a trading position, optimized for efficient calculation and visualization of
    entry, exit, and risk management strategies. Supports both long and short positions.

    Attributes:
        start_date (pd.Timestamp): The date the position is opened.
        stop_loss (float): The stop-loss level as a percentage of the entry price.
        take_profit (float): The take-profit level as a percentage of the entry price.
        market (pd.DataFrame): The market data containing at least 'close' prices.
        units (float): The number of units involved in the position.
        entry_price (float): The price at which the position is entered.
        position_type (str): Specifies the position type, either 'long' or 'short'.

    Methods:
        __post_init__: Validates the market data and computes initial values for triggers and exit information.
        validate_market_data: Ensures the market DataFrame contains a 'close' column.
        compute_triggers: Calculates the stop-loss and take-profit trigger levels and dates.
        compute_exit_info: Determines the exit price, date, and profit or loss for the position.
        plot: Visualizes the position's lifecycle on the market data, highlighting key levels and events.

    Example:
        >>> market_data = pd.DataFrame({'close': [...]}, index=pd.date_range(start="2020-01-01", periods=100))
        >>> position = OptimizedPosition(
                start_date="2020-01-10",
                stop_loss=0.05,
                take_profit=0.1,
                market=market_data,
                units=100,
                entry_price=50,
                position_type='long'
            )
        >>> position.plot()
    """
    start_date: pandas.Timestamp
    stop_loss: float
    take_profit: float
    market: pandas.DataFrame
    units: float
    entry_price: float
    position_type: str  # 'long' or 'short'

    def __post_init__(self):
        self.start_date = pandas.to_datetime(self.start_date)

        self.validate_market_data()
        self.compute_triggers()
        self.entry_value = self.entry_price * self.units
        self.generate_holding_time()

    def validate_market_data(self) -> NoReturn:
        """
        Validates that the market data provided contains a 'close' column.
        Raises:
            ValueError: If the 'close' column is not present in the market DataFrame.
        """
        if 'close' not in self.market.columns:
            raise ValueError("The market DataFrame must contain a 'close' column.")

    def update_portfolio_dataframe(self, dataframe: pandas.DataFrame) -> NoReturn:
        """
        Updates the given portfolio DataFrame with details about the trading position, including units held, holding value,
        position status (long or short), and cash balance adjustments.

        Parameters:
            dataframe (pandas.DataFrame): The portfolio DataFrame to be updated with the trading position's details.
        """
        self.add_holding_to_dataframe(dataframe=dataframe)
        self.add_position_to_dataframe(dataframe=dataframe)
        self.add_units_to_dataframe(dataframe=dataframe)
        self.update_cash(dataframe=dataframe)

    def add_position_to_dataframe(self, dataframe: pandas.DataFrame) -> NoReturn:
        """
        Marks the trading position as either long or short in the specified portfolio DataFrame during the holding period.

        Parameters:
            dataframe (pandas.DataFrame): The portfolio DataFrame to be updated with the position type information.
        """
        if self.position_type == 'short':
            dataframe.loc[self.start_date:self.stop_date, 'short_positions'] += 1
        else:
            dataframe.loc[self.start_date:self.stop_date, 'long_positions'] += 1

    def add_total_position_to_dataframe(self, dataframe: pandas.DataFrame) -> NoReturn:
        """
        Marks the trading position as either long or short in the specified portfolio DataFrame during the holding period.

        Parameters:
            dataframe (pandas.DataFrame): The portfolio DataFrame to be updated with the position type information.
        """
        dataframe.loc[self.start_date:self.stop_date, 'open_positions'] += 1

    def add_units_to_dataframe(self, dataframe: pandas.DataFrame) -> NoReturn:
        """
        Marks the trading position as either long or short in the specified portfolio DataFrame during the holding period.

        Parameters:
            dataframe (pandas.DataFrame): The portfolio DataFrame to be updated with the position type information.
        """
        dataframe.loc[self.start_date:self.stop_date, 'units'] += self.units

    def add_holding_to_dataframe(self, dataframe: pandas.DataFrame) -> NoReturn:
        """
        Adds the holding value of the trading position to the specified portfolio DataFrame during the holding period.

        Parameters:
            dataframe (pandas.DataFrame): The portfolio DataFrame to be updated with holding value information.
        """
        dataframe.loc[self.start_date:self.stop_date, 'holdings'] += self.units * self.market.close

    def update_cash(self, dataframe: pandas.DataFrame) -> NoReturn:
        """
        Updates the cash balance within a portfolio DataFrame based on the entry and exit of the trading position.

        Parameters:
            dataframe (pandas.DataFrame): The portfolio DataFrame to be updated with cash balance changes.
        """
        self.exit_price = self.market.shift().loc[self.stop_date, 'close'] if self.stop_date else numpy.nan

        entry_spend = self.entry_price * self.units
        exit_get = self.exit_price * self.units

        dataframe.loc[self.start_date:, 'cash'] -= entry_spend

        idx = dataframe.index.get_loc(self.stop_date) + 1

        dataframe.iloc[idx:, dataframe.columns.get_loc('cash')] += exit_get

    def compute_triggers(self) -> NoReturn:
        """
        Computes the trigger levels and dates for stop-loss and take-profit based on the market data and the position type.
        Sets the respective attributes for stop-loss and take-profit prices, as well as the earliest trigger date.
        """
        market_after_start = self.market.close.loc[self.start_date:]
        if self.position_type == 'short':
            self.stop_loss_price = self.entry_price * (1 + self.stop_loss)
            self.take_profit_price = self.entry_price * (1 - self.take_profit)
            condition_for_stop = market_after_start >= self.stop_loss_price
            condition_for_profit = market_after_start <= self.take_profit_price
        else:  # long position
            self.stop_loss_price = self.entry_price * (1 - self.stop_loss)
            self.take_profit_price = self.entry_price * (1 + self.take_profit)
            condition_for_stop = market_after_start <= self.stop_loss_price
            condition_for_profit = market_after_start >= self.take_profit_price

        self.stop_loss_trigger = market_after_start[condition_for_stop].first_valid_index()
        self.take_profit_trigger = market_after_start[condition_for_profit].first_valid_index()
        self.stop_date = min(filter(pandas.notna, [self.stop_loss_trigger, self.take_profit_trigger, self.market.index[-1]]))

    def generate_holding_time(self) -> NoReturn:
        """
        Generates a holding period series for the trading position, marking the period from the start date to the stop date
        within the market data timeframe. This series is used for visualization and analysis purposes.
        """
        self.holding = pandas.Series(0, index=self.market.index)
        self.holding.loc[self.start_date:self.stop_date] = 1

    def _add_stop_loss_to_ax(self, ax: plt.Axes) -> NoReturn:
        """
        Adds a horizontal line to a matplotlib axis to visualize the stop-loss level of the trading position.

        Parameters:
            ax (plt.Axes): The matplotlib axis object where the stop-loss level will be visualized.
        """
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

    def _add_triggers_to_ax(self, ax: plt.Axes) -> NoReturn:
        """
        Marks the triggers for stop-loss and take-profit on a given matplotlib axis with scatter points.

        Parameters:
            ax (plt.Axes): The matplotlib axis object where the trigger events will be visualized.
        """
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

    def _add_holding_area_to_ax(self, ax: plt.Axes) -> NoReturn:
        """
        Highlights the holding period of the trading position on a given matplotlib axis using a fill_between operation.

        Parameters:
            ax (plt.Axes): The matplotlib axis object where the holding period will be visualized.
        """
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
        """
        Generates and displays a matplotlib plot visualizing the lifecycle of the trading position. The plot includes
        the market price, entry and exit points, stop-loss and take-profit levels, and the holding period.
        """
        ax = self.market.close.plot(
            figsize=(10, 6),
            title='Position Overview',
            label='Market Close'
        )

        self._add_holding_area_to_ax(ax=ax)
        self._add_triggers_to_ax(ax=ax)
        self._add_stop_loss_to_ax(ax=ax)
        plt.legend()
        plt.show()

# -
