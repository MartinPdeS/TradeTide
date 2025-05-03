
from typing import Optional, Union

import matplotlib.pyplot as plt
from MPSPlots.styles import mps
from datetime import datetime, timedelta
import pathlib
from TradeTide import directories
from TradeTide.binary import interface_market
import re

from TradeTide.currencies import Currency
# database taken from https://forexsb.com/historical-forex-data

class Market(interface_market.Market):
    def __init__(self):
        self.currency_pair = None
        self.time_span = None
        super().__init__()

    def _parse_timespan(self, time_span) -> timedelta:
        if isinstance(time_span, timedelta):
            return time_span

        if not isinstance(time_span, str):
            raise TypeError(f"time_span must be timedelta or str, got {type(time_span)}")

        # Match one or more “number+unit” chunks, e.g. “3days”, “ 20 minutes”, “1d 2h”
        pattern = re.compile(r"(?P<value>\d+)\s*(?P<unit>d(?:ays?)?|h(?:ours?)?|m(?:inutes?)?|s(?:econds?)?)", re.I)
        parts = pattern.findall(time_span)
        if not parts:
            raise ValueError(f"Could not parse time span: {time_span!r}")

        delta = timedelta()
        for value, unit in parts:
            v = int(value)
            u = unit.lower()
            if u.startswith("d"):
                delta += timedelta(days=v)
            elif u.startswith("h"):
                delta += timedelta(hours=v)
            elif u.startswith("m"):
                delta += timedelta(minutes=v)
            elif u.startswith("s"):
                delta += timedelta(seconds=v)
        return delta

    def get_data_path(self, currency_0: Currency, currency_1: Currency, year: int) -> pathlib.Path:
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

        if not data_file.with_suffix('.csv').exists():
            data_file = data_folder / f"{currency_1}_{currency_0}" / str(year) / "data"

        return data_file


    def load_from_database(
        self,
        currency_0: Currency,
        currency_1: Currency,
        year: str,
        time_span: Union[str, timedelta],
        spread_override: Optional[float] = None,
        is_bid_override: Optional[bool] = None,
        price_type: str = "open"
    ) -> None:
        """Load market data for a currency pair from CSV, with optional overrides.

        This method constructs the CSV filename from the given currency pair and
        start_date.year, parses the provided time span (allowing either a `timedelta`
        or a human‐friendly string like "3days" or "4h30m"), then invokes
        `load_from_csv(...)` with optional overrides for spread and bid/ask flag.
        Finally, it selects which price series to use (open/close/high/low).

        Args:
            currency_0 (Currency): The base currency of the pair (e.g. Currency.EUR).
            currency_1 (Currency): The quote currency of the pair (e.g. Currency.USD).
            start_date (datetime): Any datetime within the year whose data file to load.
            time_span (Union[str, timedelta]): Amount of history to load starting at the
                first timestamp; may be a `timedelta` or a string like "2d 6h".
            spread_override (Optional[float]): If given, every row’s spread is set to this
                value instead of the file’s spread column or default.
            is_bid_override (Optional[bool]): If given, sets the market’s bid/ask flag
                regardless of any `#is_bid=` metadata in the CSV.
            price_type (str): Which price series to expose for trading logic; must be one
                of "open", "close", "high", or "low".

        Raises:
            FileNotFoundError: If the constructed CSV path does not exist or cannot be opened.
            ValueError: If `time_span` cannot be parsed or `price_type` is invalid.
            RuntimeError: On CSV parsing errors (malformed lines, missing columns, etc.).
        """
        # 1) Normalize time_span to a timedelta
        ts = self._parse_timespan(time_span)
        self.time_span = ts

        # 2) Build currency pair identifier and CSV path
        self.currency_pair = f"{currency_0.value}/{currency_1.value}"
        csv_path = self.get_data_path(
            currency_0=currency_0.value,
            currency_1=currency_1.value,
            year=year
        ).with_suffix(".csv")

        self.load_from_csv(
            filename=str(csv_path),
            time_span=ts,
            spread_override=spread_override,
            is_bid_override=is_bid_override,
        )

        # 5) Select the desired price series
        self.set_price_type(price_type)


    def plot(self) -> None:
        plt.style.use(mps)
        figure, ax = plt.subplots(1, 1)

        plt.plot(
            self.dates,
            self.ask.open,
            label="Ask-open",
        )

        plt.plot(
            self.dates,
            self.bid.open,
            label="Bid-open",
        )


        ax.set_xlabel("Time")
        ax.set_ylabel("Price")
        ax.set_title(f"{self.currency_pair} - {self.time_span}")
        ax.legend()
        plt.show()