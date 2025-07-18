
from typing import Union

import matplotlib.pyplot as plt
from MPSPlots.styles import mps
from datetime import timedelta
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

    def get_data_path(self, currency_0: Currency, currency_1: Currency) -> pathlib.Path:
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

        data_file = data_folder / f"{currency_0}_{currency_1}.csv"

        if not data_file.with_suffix('.csv').exists():
            data_file = data_folder / f"{currency_1}_{currency_0}"

        return data_file


    def load_from_database(self, currency_0: Currency, currency_1: Currency, time_span: Union[str, timedelta]) -> None:
        """Load market data for a currency pair from CSV, with optional overrides.

        This method constructs the CSV filename from the given currency pair and
        start_date.year, parses the provided time span (allowing either a `timedelta`
        or a human-friendly string like "3days" or "4h30m"), then invokes
        `load_from_csv(...)` with optional overrides for spread and bid/ask flag.
        Finally, it selects which price series to use (open/close/high/low).

        Args:
            currency_0 (Currency): The base currency of the pair (e.g. Currency.EUR).
            currency_1 (Currency): The quote currency of the pair (e.g. Currency.USD).
            start_date (datetime): Any datetime within the year whose data file to load.
            time_span (Union[str, timedelta]): Amount of history to load starting at the
                first timestamp; may be a `timedelta` or a string like "2d 6h".

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
        ).with_suffix(".csv")

        self.load_from_csv(
            filename=str(csv_path),
            time_span=ts
        )

    def plot_ask(self, ax: plt.Axes = None, show: bool = True) -> None:
        """
        Plot low-high ranges as filled bands with step="pre",
        and open-close as solid/dashed step lines for Ask.
        """
        if ax is None:
            plt.style.use(mps)
            _, ax = plt.subplots(figsize=(12, 6))

        # -----------------------------------------------------------------------------
        # 1. Fill between low and high with a lightly shaded band
        # -----------------------------------------------------------------------------
        ax.fill_between(
            self.dates,
            self.ask.low,
            self.ask.high,
            step="pre",
            alpha=0.2,
            color="blue",
            label="Ask Low-High"
        )

        # -----------------------------------------------------------------------------
        # 2. Plot open and close as step lines
        # -----------------------------------------------------------------------------
        ax.plot(
            self.dates,
            self.ask.open,
            drawstyle="steps-pre",
            color="blue",
            linestyle="-",    # solid line for Open
            label="Ask Open"
        )
        ax.plot(
            self.dates,
            self.ask.close,
            drawstyle="steps-pre",
            color="blue",
            linestyle=":",    # dashed line for Close
            label="Ask Close"
        )

        # -----------------------------------------------------------------------------
        # 3. Final formatting
        # -----------------------------------------------------------------------------
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")
        ax.set_title(f"{self.currency_pair} - {self.time_span}")
        ax.legend(loc="upper left")

        if show:
            plt.tight_layout()
            plt.show()


    def plot_bid(self, ax: plt.Axes = None, show: bool = True) -> None:
        """
        Plot low-high ranges as filled bands with step="pre",
        and open-close as solid/dashed step lines for Bid.
        """
        if ax is None:
            plt.style.use(mps)
            _, ax = plt.subplots(figsize=(12, 6))

        # -----------------------------------------------------------------------------
        # 1. Fill between low and high with a lightly shaded band
        # -----------------------------------------------------------------------------
        ax.fill_between(
            self.dates,
            self.bid.low,
            self.bid.high,
            step="pre",
            alpha=0.2,
            color="orange",
            label="Bid Low-High"
        )

        # -----------------------------------------------------------------------------
        # 2. Plot open and close as step lines
        # -----------------------------------------------------------------------------
        ax.plot(
            self.dates,
            self.bid.open,
            drawstyle="steps-pre",
            color="orange",
            linestyle="-",    # solid line for Open
            label="Bid Open"
        )
        ax.plot(
            self.dates,
            self.bid.close,
            drawstyle="steps-pre",
            color="orange",
            linestyle=":",    # dashed line for Close
            label="Bid Close"
        )

        # -----------------------------------------------------------------------------
        # 3. Final formatting
        # -----------------------------------------------------------------------------
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")
        ax.set_title(f"{self.currency_pair} - {self.time_span}")
        ax.legend(loc="upper left")

        if show:
            plt.tight_layout()
            plt.show()

    def plot(self, ax: plt.Axes = None, show_ask: bool = True, show_bid: bool = True, show: bool = True) -> None:
        """
        Plot low-high ranges as filled bands with step="pre",
        and open-close as solid/dashed step lines for Ask and Bid.
        """
        if ax is None:
            plt.style.use(mps)
            _, ax = plt.subplots(figsize=(12, 6))

        # -----------------------------------------------------------------------------
        # 1. Ask: fill between low and high with a lightly shaded band
        # -----------------------------------------------------------------------------
        if show_ask:
            self.plot_ask(ax=ax, show=False)

        # -----------------------------------------------------------------------------
        # 3. Bid: fill between low and high with a lightly shaded band (shift color)
        # -----------------------------------------------------------------------------
        if show_bid:
            self.plot_bid(ax=ax, show=False)

        # -----------------------------------------------------------------------------
        # 5. Final formatting
        # -----------------------------------------------------------------------------
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")
        ax.set_title(f"{self.currency_pair} - {self.time_span}")
        ax.legend(loc="upper left")


        if show:
            plt.tight_layout()
            plt.show()
