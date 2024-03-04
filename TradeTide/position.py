#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from typing import NoReturn
import pandas
import numpy
import matplotlib.pyplot as plt

from dataclasses import dataclass
from TradeTide.risk_management import LossProfitManagementBase


@dataclass
class Position:
    """
    Represents a financial trading position with functionality for risk management,
    performance analysis, and visualization. It incorporates both long and short positions,
    taking into account entry and exit strategies based on predefined risk management parameters.

    Attributes:
        start_date (pd.Timestamp): Date when the position is initiated.
        market (pd.DataFrame): DataFrame containing market data with at least 'close' and 'spread' prices.
        position_type (str): Type of the position ('long' or 'short').
        risk_management (LossProfitManagementBase): An instance of a risk management strategy defining stop loss and take profit levels.
        maximum_cash (float): The maximum amount of cash allocated for this position.

    The class requires market data and a risk management strategy to initialize. It calculates
    the entry price, number of units, and cost at initiation. It also computes the precise levels
    for stop loss and take profit based on the provided strategy and market conditions at the start date.

    Methods:
        initialize(): Prepares the position by setting stop loss and take profit prices based on the risk management strategy.
        update_portfolio_dataframe(dataframe: pd.DataFrame): Updates a given portfolio DataFrame with the position's details.
        compute_exit_info(): Calculates the exit price based on market data and updates the cash balance accordingly.
        compute_triggers(): Identifies trigger points for stop loss and take profit based on market movements post-entry.
        plot(): Visualizes the position lifecycle on a price chart, highlighting key events and levels.

    Usage Example:
        >>> market_data = pd.DataFrame({
                'close': [1.10, 1.15, 1.08, 1.12, 1.15],
                'spread': [0.01, 0.01, 0.01, 0.01, 0.01]
            }, index=pd.date_range(start="2020-01-01", periods=5))
        >>> risk_strategy = LossProfitManagementBase(stop_loss=0.05, take_profit=0.1)
        >>> position = Position(
                start_date=pd.Timestamp("2020-01-01"),
                market=market_data,
                position_type='long',
                risk_management=risk_strategy,
                maximum_cash=1000
            )
        >>> position.initialize()
        >>> position.plot()

    This class simplifies the management of trading positions by automating risk calculations and providing
    visual insights into the trading strategy's execution, making it an essential tool for backtesting trading strategies.
    """
    start_date: pandas.Timestamp
    market: pandas.DataFrame
    position_type: str  # 'long' or 'short'
    risk_management: LossProfitManagementBase
    maximum_cash: float

    def __post_init__(self):
        # Initial setup: calculates entry price, units, and validates position feasibility.
        self.spread = self.market.spread[self.start_date]
        self.entry_price = self.market.close[self.start_date]

        self.units = (self.maximum_cash - self.spread) / self.entry_price

        self.cost = self.units * self.entry_price + self.spread

        if self.units < 1:
            self.is_valid = False

        self.is_valid = True

    def initialize(self) -> NoReturn:
        self.stop_loss_price, self.take_profit_price = self.risk_management.get_loss_profit_price(
            position_type=self.position_type,
            entry_price=self.entry_price
        )

        self.compute_triggers()
        self.entry_value = self.entry_price * self.units
        self.generate_holding_time()

    @property
    def profit_loss(self) -> float:
        """ Retunrs the cash value that this position made over time """
        return self.exit_get - self.entry_spend

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

    def compute_exit_info(self) -> None:
        """
        Determines and sets the exit price of the position based on market data and the position type.
        This is a placeholder method; the actual implementation should compute the exit price.
        """
        self.exit_price = self.market.shift().loc[self.stop_date, 'close'] if self.stop_date else numpy.nan

    def update_cash(self, dataframe: pandas.DataFrame) -> NoReturn:
        """
        Updates the cash balance within a portfolio DataFrame based on the entry and exit of the trading position.

        Parameters:
            dataframe (pandas.DataFrame): The portfolio DataFrame to be updated with cash balance changes.
        """
        self.compute_exit_info()

        self.entry_spend = self.entry_price * self.units
        self.exit_get = self.exit_price * self.units

        dataframe.loc[self.start_date:, 'cash'] -= self.entry_spend

        idx = dataframe.index.get_loc(self.stop_date) + 1

        dataframe.iloc[idx:, dataframe.columns.get_loc('cash')] += self.exit_get

    def compute_triggers(self) -> NoReturn:
        """
        Computes the trigger levels and dates for stop-loss and take-profit based on the market data and the position type.
        Sets the respective attributes for stop-loss and take-profit prices, as well as the earliest trigger date.
        """
        market_after_start = self.market.close.loc[self.start_date:]
        if self.position_type == 'short':
            condition_for_stop = market_after_start >= self.stop_loss_price
            condition_for_profit = market_after_start <= self.take_profit_price
        else:  # long position
            condition_for_stop = market_after_start <= self.stop_loss_price
            condition_for_profit = market_after_start >= self.take_profit_price

        self.stop_loss_trigger = market_after_start[condition_for_stop].first_valid_index()
        self.take_profit_trigger = market_after_start[condition_for_profit].first_valid_index()
        self.stop_date = min(filter(pandas.notna, [self.stop_loss_trigger, self.take_profit_trigger, self.market.index[-1]]))

    @property
    def is_win(self) -> int:
        """
        Determines the outcome of the position.

        Returns:
            int: 0 if neither stop loss nor take profit is triggered,
                 +1 if take profit is triggered first,
                 -1 if stop loss is triggered first.
        """
        # Ensure both triggers are computed, they could be None if not triggered
        stop_loss_triggered = self.stop_loss_trigger is not None
        take_profit_triggered = self.take_profit_trigger is not None

        # If neither is triggered, return 0
        if not stop_loss_triggered and not take_profit_triggered:
            return 0
        # If stop loss is triggered but take profit isn't, or it's triggered first
        if stop_loss_triggered and (not take_profit_triggered or self.stop_loss_trigger < self.take_profit_trigger):
            return -1
        # If take profit is triggered but stop loss isn't, or it's triggered first
        if take_profit_triggered and (not stop_loss_triggered or self.take_profit_trigger < self.stop_loss_trigger):
            return +1

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
        Visualizes the trading position on a price chart. Highlights include the entry and exit points,
        stop loss and take profit levels, and the duration of the position. This method provides a graphical
        overview of the position's performance within the market context.
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
