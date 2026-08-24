from typing import Union
import matplotlib.pyplot as plt
from MPSPlots import helper
from datetime import timedelta
import pathlib
import re


from TradeTide import directories
from TradeTide.currencies import Currency
from TradeTide.binary import interface_market

# database taken from https://forexsb.com/historical-forex-data


class Market(interface_market.Market):
    def __init__(self):
        self.currency_pair = None
        self.time_span = None
        super().__init__()

    def _parse_timespan(self, time_span) -> timedelta:
        if isinstance(time_span, timedelta):
            delta = time_span
        else:
            if not isinstance(time_span, str):
                raise TypeError(
                    "time_span must be a datetime.timedelta or a duration string "
                    "such as '2d 6h'; "
                    f"got {type(time_span).__name__}."
                )

            # Accept one or more number/unit chunks, e.g. ``3days`` or ``1d 2h``.
            token = re.compile(
                r"(?P<value>\d+)\s*(?P<unit>d(?:ays?)?|h(?:ours?)?|m(?:inutes?)?|s(?:econds?)?)",
                re.I,
            )
            parts = token.findall(time_span)
            remainder = token.sub("", time_span).strip()
            if not parts or remainder:
                raise ValueError(
                    "time_span must be a positive duration such as '2d 6h', '90m', "
                    f"or timedelta(hours=2); got {time_span!r}."
                )

            delta = timedelta()
            for value, unit in parts:
                value_as_int = int(value)
                unit = unit.lower()
                if unit.startswith("d"):
                    delta += timedelta(days=value_as_int)
                elif unit.startswith("h"):
                    delta += timedelta(hours=value_as_int)
                elif unit.startswith("m"):
                    delta += timedelta(minutes=value_as_int)
                elif unit.startswith("s"):
                    delta += timedelta(seconds=value_as_int)

        if delta <= timedelta():
            raise ValueError("time_span must be greater than zero.")
        return delta

    @staticmethod
    def _validate_currency_pair(currency_0: Currency, currency_1: Currency) -> None:
        for parameter, currency in (("currency_0", currency_0), ("currency_1", currency_1)):
            if not isinstance(currency, Currency):
                raise TypeError(
                    f"{parameter} must be a Currency member (for example Currency.EUR); "
                    f"got {currency!r}."
                )
        if currency_0 is currency_1:
            raise ValueError(
                "currency_0 and currency_1 must be different currencies; "
                f"got {currency_0.value}/{currency_1.value}."
            )

    def get_data_path(self, currency_0: str, currency_1: str) -> pathlib.Path:
        """
        Construct the expected path to a bundled currency-pair CSV file.

        Parameters:
            currency_0: The base currency code.
            currency_1: The quote currency code.

        Returns:
            The expected path, whether or not the bundled dataset exists.
        """
        data_file = directories.data / f"{currency_0}_{currency_1}.csv"

        return data_file

    def load_from_database(
        self,
        currency_0: Currency,
        currency_1: Currency,
        time_span: Union[str, timedelta],
    ) -> None:
        """Load bundled CSV market data for a currency pair.

        Args:
            currency_0 (Currency): The base currency of the pair (e.g. Currency.EUR).
            currency_1 (Currency): The quote currency of the pair (e.g. Currency.USD).
            time_span (Union[str, timedelta]): Amount of history to load starting at the
                first timestamp; may be a `timedelta` or a string like "2d 6h".

        Raises:
            FileNotFoundError: If no bundled CSV exists for the requested pair.
            TypeError: If a currency is not a ``Currency`` member or the time span type is invalid.
            ValueError: If currencies are identical or the time span is not positive.
        """
        self._validate_currency_pair(currency_0, currency_1)
        # 1) Normalize time_span to a timedelta
        ts = self._parse_timespan(time_span)
        self.time_span = ts

        # 2) Build currency pair identifier and CSV path
        self.currency_pair = f"{currency_0.value}/{currency_1.value}"

        csv_path = self.get_data_path(
            currency_0=currency_0.value,
            currency_1=currency_1.value,
        )

        if not csv_path.is_file():
            available_pairs = sorted(
                path.stem.replace("_", "/") for path in directories.data.glob("*.csv")
            )
            raise FileNotFoundError(
                f"No bundled market data is available for {self.currency_pair}. "
                f"Available datasets: {', '.join(available_pairs)}."
            )

        self.load_from_csv(filename=str(csv_path), time_span=ts)

    @helper.pre_plot(nrows=1, ncols=1)
    def plot_ask(self, axes: plt.Axes = None) -> None:
        """
        Plot low-high ranges as filled bands with step="pre",
        and open-close as solid/dashed step lines for Ask.
        """

        # 1. Fill between low and high with a lightly shaded band

        axes.fill_between(
            self.dates,
            self.ask.low,
            self.ask.high,
            step="pre",
            alpha=0.2,
            color="blue",
            label="Ask Low-High",
        )

        # 2. Plot open and close as step lines

        axes.plot(
            self.dates,
            self.ask.open,
            drawstyle="steps-pre",
            color="blue",
            linestyle="-",  # solid line for Open
            label="Ask Open",
        )
        axes.plot(
            self.dates,
            self.ask.close,
            drawstyle="steps-pre",
            color="blue",
            linestyle=":",  # dashed line for Close
            label="Ask Close",
        )

        # 3. Final formatting

        axes.set_xlabel("Time")
        axes.set_ylabel("Price")
        axes.set_title(f"{self.currency_pair} - {self.time_span}")
        axes.legend(loc="upper left")

    @helper.pre_plot(nrows=1, ncols=1)
    def plot_bid(self, axes: plt.Axes) -> None:
        """
        Plot low-high ranges as filled bands with step="pre",
        and open-close as solid/dashed step lines for Bid.

        Parameters
        ----------
        axes : matplotlib.axes.Axes
            Axes to draw on. If None, a new figure+axes are created.
        """
        # 1. Fill between low and high with a lightly shaded band
        axes.fill_between(
            self.dates,
            self.bid.low,
            self.bid.high,
            step="pre",
            alpha=0.2,
            color="orange",
            label="Bid Low-High",
        )

        # 2. Plot open and close as step lines
        axes.plot(
            self.dates,
            self.bid.open,
            drawstyle="steps-pre",
            color="orange",
            linestyle="-",  # solid line for Open
            label="Bid Open",
        )
        axes.plot(
            self.dates,
            self.bid.close,
            drawstyle="steps-pre",
            color="orange",
            linestyle=":",  # dashed line for Close
            label="Bid Close",
        )

        # 3. Final formatting
        axes.set_xlabel("Time")
        axes.set_ylabel("Price")
        axes.set_title(f"{self.currency_pair} - {self.time_span}")
        axes.legend(loc="upper left")

    @helper.pre_plot(nrows=1, ncols=1)
    def plot(self, axes: plt.Axes) -> None:
        """
        Plot low-high ranges as filled bands with step="pre",
        and open-close as solid/dashed step lines for Ask and Bid.

        Parameters
        ----------
        axes : matplotlib.axes.Axes
            Axes to draw on. If None, a new figure+axes are created.
        """
        self.plot_ask(axes=axes, show=False)

        self.plot_bid(axes=axes, show=False)

        axes.set_xlabel("Time")
        axes.set_ylabel("Price")
        axes.set_title(f"{self.currency_pair} - {self.time_span}")
        axes.legend(loc="upper left")
