#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from typing import NoReturn

from TradeTide import directories
import pandas
import pathlib

# data taken from https://forexsb.com/historical-forex-data


def get_data_path(currency_0: str, currency_1: str, year: int) -> pathlib.Path:
    """
    Constructs a pathlib.Path object pointing to the data file for a given currency pair and year.

    The path is constructed using a predefined directory structure from the `directories` module, assuming the data is
    stored in a specific format: `<base_dir>/<currency_0>_<currency_1>/<year>/data`.

    Parameters:
        currency_0 (str): The base currency of the currency pair.
        currency_1 (str): The quote currency of the currency pair.
        year (int): The year for which the data is required.

    Returns:
        pathlib.Path: The path to the data file for the specified currency pair and year.
    """
    data_folder = directories.data

    data_file = data_folder / f"{currency_0}_{currency_1}" / str(year) / "data"

    return data_file


def get_market_data(currency_0: str, currency_1: str, year: int) -> pandas.DataFrame:
    """
    Reads currency exchange data from a CSV file into a pandas DataFrame and processes it.

    The function reads the data from a CSV file corresponding to the specified currency pair and year, converts the
    'date' column to datetime, checks that the dates are in increasing order, converts the 'date' column to UTC timezone,
    and calculates time deltas between consecutive entries.

    Parameters:
        currency_0 (str): The base currency of the currency pair.
        currency_1 (str): The quote currency of the currency pair.
        year (int): The year of the data.

    Returns:
        pandas.DataFrame: The processed DataFrame containing the currency exchange data.
    """
    data_file = get_data_path(
        currency_0=currency_0,
        currency_1=currency_1,
        year=year
    )

    dataframe = pandas.read_csv(
        filepath_or_buffer=data_file.with_suffix('.csv'),
        names=['date', 'open', 'high', 'low', 'close', 'volume', 'spread']
    )

    dataframe['date'] = pandas.to_datetime(dataframe['date'])

    assert dataframe['date'].is_monotonic_increasing, 'Time stamp is not monotonic increasing'

    dataframe['date'] = dataframe['date'].dt.tz_localize('UTC')

    dataframe['time_stamp'] = pandas.to_timedelta(dataframe['date'].diff())

    dataframe['time_delta'] = dataframe['date'].diff()

    dataframe = dataframe.set_index('date')

    return dataframe


def convert_xlsx_to_csv(currency_0: str, currency_1: str, year: int) -> NoReturn:
    """
    Converts an Excel file containing currency data to a CSV format.

    This function reads currency data for the specified currency pair and year from an Excel file, sets the column names
    to a predefined list, and saves the data to a CSV file in the same location as the original Excel file.

    Parameters:
        currency_0 (str): The base currency of the currency pair.
        currency_1 (str): The quote currency of the currency pair.
        year (int): The year of the data.

    Returns:
        None
    """
    data_file = get_data_path(
        currency_0=currency_0,
        currency_1=currency_1,
        year=year
    )

    dataframe = pandas.read_excel(data_file.with_suffix('.xlsx'))

    columns = [
        'date', 'open', 'high', 'low', 'close', 'volume'
    ]

    dataframe.columns = columns

    dataframe.to_csv(data_file.with_suffix('.csv'), index=False)

# -