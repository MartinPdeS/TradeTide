#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from typing import NoReturn
import pandas
import numpy
from TradeTide.position import Position
from TradeTide.tools import percent_to_float


class CapitalManagement:
    """
    A base class for managing capital in a trading environment. It defines common properties
    and methods used by subclasses for specific capital management strategies.
    """

    def __init__(self, spread: float, stop_loss: float, take_profit: float, max_cap_per_trade: float):
        """
        Initializes the CapitalManagement object with common trading parameters.

        Parameters:
        - spread (float): The cost as a spread applied to the entry price of each new position.
        - stop_loss (float): The stop loss percentage, indicating the maximum loss acceptable before closing a position.
        - take_profit (float): The take profit percentage, indicating the target profit to close a position.
        - max_cap_per_trade (float): The maximum capital allocated for each trade.
        """
        self.spread = spread
        self.stop_loss = percent_to_float(stop_loss)
        self.take_profit = percent_to_float(take_profit)
        self.max_cap_per_trade = max_cap_per_trade

    def manage(self, backtester: object, market: pandas.DataFrame) -> NoReturn:
        """
        Manages trading positions based on the strategy's signals, market data, and the subclass's
        specific capital management strategy. This method should be implemented by subclasses.

        Parameters:
        - backtester (object): The backtesting framework instance.
        - market (pd.DataFrame): The market data containing historical price information.
        """
        raise NotImplementedError("Subclasses should implement this method.")


class LimitedCapital(CapitalManagement):
    """
    Manages trading capital with a limitation on the initial capital and the maximum number of open positions.
    """

    def __init__(
            self,
            spread: float,
            stop_loss: float,
            take_profit: float,
            initial_capital: float,
            max_cap_per_trade: float,
            limit_of_positions: int = numpy.inf):
        """
        Initializes the LimitedCapital object with trading parameters and limitations on capital and positions.

        Parameters:
        - initial_capital (float): The initial capital available for trading.
        - limit_of_positions (int): The maximum number of positions that can be open at any time.
        """
        super().__init__(spread, stop_loss, take_profit, max_cap_per_trade)
        self.initial_capital = initial_capital
        self.limit_of_positions = limit_of_positions

    def manage(self, backtester: object, market: pandas.DataFrame) -> NoReturn:
        """
        Implements the capital management strategy for a trading scenario with limited capital and positions.

        Parameters:
        - backtester (object): The backtesting framework instance.
        - market (pd.DataFrame): The market data containing historical price information.
        """
        self.time_info = pandas.DataFrame(index=market.index, columns=['cash'])
        self.time_info['cash'] = float(self.initial_capital)
        self.time_info['open_positions'] = int(0)

        # Detect new positions based on strategy signals
        signals = backtester.strategy.signal
        new_positions_idx = signals[signals.diff().fillna(0) != 0].index

        # Initialize or clear the list to store Position objects
        backtester.position_list = []

        # Iterate over signals and open new positions where indicated
        for date in new_positions_idx:

            cash_at_date: float = self.time_info.cash[date]
            open_postion_at_date: int = self.time_info.open_positions[date]

            if backtester.strategy.signal.loc[date] != 0:  # Ensure there's an actionable signal

                entry_price: float = backtester.market.loc[date, 'close'] + self.spread

                units: int = numpy.floor(
                    min((self.max_cap_per_trade - self.spread) / entry_price, (cash_at_date - self.spread) / entry_price)
                )

                if open_postion_at_date >= self.limit_of_positions:
                    continue

                if units < 1.0:
                    continue

                # Calculate the cost of the new position
                position_cost: float = units * entry_price + self.spread

                # Check if there's enough cash to open the position
                if cash_at_date < position_cost:
                    print(f"Insufficient cash to open a new position on {date}. Available cash: {self.cash}")
                    continue

                position_type: str = 'long' if backtester.strategy.signal.loc[date] > 0 else 'short'

                position = Position(
                    start_date=date,
                    stop_loss=self.stop_loss,
                    take_profit=self.take_profit,
                    market=market,
                    units=units,
                    entry_price=entry_price,
                    position_type=position_type
                )

                position.update_cash(dataframe=self.time_info)
                position.add_total_position_to_dataframe(dataframe=self.time_info)

                backtester.position_list.append(position)


class UnlimitedCapital(CapitalManagement):
    """
    Manages trading capital without limitations on the initial capital or the number of open positions.
    """

    def __init__(
            self,
            spread: float,
            stop_loss: float,
            take_profit: float,
            max_cap_per_trade: float):
        """
        Initializes the UnlimitedCapital object with trading parameters.
        """
        super().__init__(spread, stop_loss, take_profit, max_cap_per_trade)

    def manage(self, backtester: object, market: pandas.DataFrame) -> NoReturn:
        """
        Implements the capital management strategy for a trading scenario without capital and position limits.

        Parameters:
        - backtester (object): The backtesting framework instance.
        - market (pd.DataFrame): The market data containing historical price information.
        """
        # Detect new positions based on strategy signals
        signals = backtester.strategy.signal
        new_positions_idx = signals[signals.diff().fillna(0) != 0].index

        # Initialize or clear the list to store Position objects
        backtester.position_list = []

        # Iterate over signals and open new positions where indicated
        for date in new_positions_idx:

            if backtester.strategy.signal.loc[date] != 0:

                entry_price: float = backtester.market.loc[date, 'close'] + self.spread

                units: int = (self.max_cap_per_trade - self.spread) / entry_price
                units = numpy.floor(units)

                if units < 1.0:
                    continue

                position_type: str = 'long' if backtester.strategy.signal.loc[date] > 0 else 'short'

                position = Position(
                    start_date=date,
                    stop_loss=self.stop_loss,
                    take_profit=self.take_profit,
                    market=market,
                    units=units,
                    entry_price=entry_price,
                    position_type=position_type
                )

                position.update_cash(dataframe=backtester.portfolio)

                backtester.position_list.append(position)


# -
