#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from typing import NoReturn
import pandas
import numpy
from TradeTide.position import Position
from TradeTide.loss_profit_managment import DirectLossProfitManagement, ATRLossProfitManagement


class CapitalManagement:
    """
    A base class for managing capital in a trading environment. It defines common properties
    and methods used by subclasses for specific capital management strategies.
    """

    def __init__(
            self,
            spread: float,
            loss_profit_managment: DirectLossProfitManagement | ATRLossProfitManagement,
            max_cap_per_trade: float,
            limit_of_positions: int = numpy.inf):
        """
        Initializes the CapitalManagement object with common trading parameters.

        Parameters:
            - spread (float): The cost as a spread applied to the entry price of each new position.
            - stop_loss (float): The stop loss percentage, indicating the maximum loss acceptable before closing a position.
            - take_profit (float): The take profit percentage, indicating the target profit to close a position.
            - max_cap_per_trade (float): The maximum capital allocated for each trade.
            - limit_of_positions (int): The maximum number of positions that can be open at any time.
        """
        self.spread = spread
        self.max_cap_per_trade = max_cap_per_trade
        self.limit_of_positions = limit_of_positions
        self.loss_profit_managment = loss_profit_managment

    def manage(self, backtester: object, market: pandas.DataFrame) -> NoReturn:
        """
        Manages trading positions based on the strategy's signals, market data, and the subclass's
        specific capital management strategy. This method should be implemented by subclasses.

        Parameters:
            - backtester (object): The backtesting framework instance.
            - market (pandas.DataFrame): The market data containing historical price information.
        """
        raise NotImplementedError("Subclasses should implement this method.")


class LimitedCapital(CapitalManagement):
    """
    Manages trading capital with a limitation on the initial capital and the maximum number of open positions.
    """

    def __init__(
            self,
            spread: float,
            loss_profit_managment: DirectLossProfitManagement | ATRLossProfitManagement,
            initial_capital: float,
            max_cap_per_trade: float,
            limit_of_positions: int = numpy.inf):
        """
        Initializes the LimitedCapital object with trading parameters and limitations on capital and positions.

        Parameters:
            - initial_capital (float): The initial capital available for trading.
        """
        super().__init__(
            spread=spread,
            loss_profit_managment=loss_profit_managment,
            max_cap_per_trade=max_cap_per_trade,
            limit_of_positions=limit_of_positions
        )

        self.initial_capital = initial_capital
        self.limit_of_positions = limit_of_positions

    def manage(self, backtester: object, market: pandas.DataFrame) -> NoReturn:
        """
        Implements the capital management strategy for a trading scenario with limited capital and positions.

        Parameters:
            - backtester (object): The backtesting framework instance.
            - market (pandas.DataFrame): The market data containing historical price information.
        """
        self.market = market

        self.time_info = pandas.DataFrame(index=market.index, columns=['cash'])
        self.time_info['cash'] = float(self.initial_capital)
        self.time_info['open_positions'] = int(0)

        # Initialize or clear the list to store Position objects
        backtester.position_list = []

        # Iterate over signals and open new positions where indicated
        for date in market.index:
            cash_at_date: float = self.time_info.cash[date]
            open_postion_at_date: int = self.time_info.open_positions[date]

            signal = backtester.strategy.signal.loc[date]
            if signal == 0 or open_postion_at_date >= self.limit_of_positions:
                continue

            entry_price = market.loc[date, 'close'] + self.spread
            units = min((self.max_cap_per_trade - self.spread) / entry_price, (cash_at_date - self.spread) / entry_price)
            if units < 1:
                continue

            position_cost = units * entry_price + self.spread
            if self.time_info.loc[date, 'cash'] < position_cost:
                continue

            position_type = 'long' if signal > 0 else 'short'

            stop_loss_price, take_profit_price = self.loss_profit_managment.get_loss_profit_price(
                position_type=position_type,
                entry_price=entry_price
            )

            position = Position(
                start_date=date,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
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
            loss_profit_managment: DirectLossProfitManagement | ATRLossProfitManagement,
            max_cap_per_trade: float,
            limit_of_positions: int = numpy.inf):
        """
        Initializes the UnlimitedCapital object with trading parameters.
        """
        super().__init__(
            spread=spread,
            loss_profit_managment=loss_profit_managment,
            max_cap_per_trade=max_cap_per_trade,
            limit_of_positions=limit_of_positions
        )

    def manage(self, backtester: object, market: pandas.DataFrame) -> NoReturn:
        """
        Implements the capital management strategy for a trading scenario without capital and position limits.

        Parameters:
            - backtester (object): The backtesting framework instance.
            - market (pandas.DataFrame): The market data containing historical price information.
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

                stop_loss_price, take_profit_price = self.loss_profit_managment.get_loss_profit_price(
                    position_type=position_type,
                    entry_price=entry_price
                )

                position = Position(
                    start_date=date,
                    stop_loss_price=stop_loss_price,
                    take_profit_price=take_profit_price,
                    market=market,
                    units=units,
                    entry_price=entry_price,
                    position_type=position_type
                )

                position.update_cash(dataframe=backtester.portfolio)

                backtester.position_list.append(position)


# -
