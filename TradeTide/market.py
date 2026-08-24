from typing import Literal, Union
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.dates import date2num
import numpy as np
from TradeTide.plotting import pre_plot
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
        for parameter, currency in (
            ("currency_0", currency_0),
            ("currency_1", currency_1),
        ):
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

    @staticmethod
    def _aggregate_ohlc(
        dates: np.ndarray,
        open_prices: np.ndarray,
        low_prices: np.ndarray,
        high_prices: np.ndarray,
        close_prices: np.ndarray,
        max_candles: int | None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Downsample OHLC data while preserving the first open and final close."""
        if max_candles is None or len(dates) <= max_candles:
            return dates, open_prices, low_prices, high_prices, close_prices
        if max_candles < 1:
            raise ValueError("max_candles must be a positive integer or None.")

        groups = np.array_split(np.arange(len(dates)), max_candles)
        return (
            np.asarray([dates[group[0]] for group in groups]),
            np.asarray([open_prices[group[0]] for group in groups]),
            np.asarray([low_prices[group].min() for group in groups]),
            np.asarray([high_prices[group].max() for group in groups]),
            np.asarray([close_prices[group[-1]] for group in groups]),
        )

    def _plot_candles(
        self,
        axes: plt.Axes,
        side: Literal["ask", "bid"],
        max_candles: int | None,
    ) -> None:
        """Draw an OHLC series with four batched Matplotlib collections."""
        prices = self.ask if side == "ask" else self.bid
        dates = np.asarray(self.dates)
        open_prices = np.asarray(prices.open, dtype=float)
        low_prices = np.asarray(prices.low, dtype=float)
        high_prices = np.asarray(prices.high, dtype=float)
        close_prices = np.asarray(prices.close, dtype=float)
        dates, open_prices, low_prices, high_prices, close_prices = (
            self._aggregate_ohlc(
                dates, open_prices, low_prices, high_prices, close_prices, max_candles
            )
        )
        x_values = date2num(dates)
        if len(x_values) == 0:
            return
        spacing = np.diff(x_values)
        width = (
            np.median(spacing[spacing > 0]) if np.any(spacing > 0) else 1 / 1_440
        ) * 0.7
        bullish = close_prices >= open_prices

        for mask, color, label in (
            (bullish, "#16a085", f"{side.title()} up"),
            (~bullish, "#e74c3c", f"{side.title()} down"),
        ):
            x = x_values[mask]
            opens = open_prices[mask]
            closes = close_prices[mask]
            lows = low_prices[mask]
            highs = high_prices[mask]
            wicks = np.stack(
                (np.column_stack((x, lows)), np.column_stack((x, highs))), axis=1
            )
            bodies = [
                (
                    (value - width / 2, opening),
                    (value + width / 2, opening),
                    (value + width / 2, closing),
                    (value - width / 2, closing),
                )
                for value, opening, closing in zip(x, opens, closes)
            ]
            axes.add_collection(LineCollection(wicks, colors=color, linewidths=0.8))
            axes.add_collection(
                PolyCollection(
                    bodies,
                    facecolors=color,
                    edgecolors=color,
                    linewidths=0.5,
                    label=label,
                )
            )

        axes.autoscale_view()

    @pre_plot(nrows=1, ncols=1)
    def plot_candles(
        self,
        axes: plt.Axes,
        side: Literal["ask", "bid"] = "ask",
        max_candles: int | None = 2_000,
    ) -> None:
        """Plot fast batched candlesticks for the ask or bid series.

        Candles are drawn as four Matplotlib collections rather than one artist
        per bar.  Large datasets are automatically aggregated into at most
        ``max_candles`` visual bars, retaining each bin's open, high, low, and
        close values.
        """
        if side not in ("ask", "bid"):
            raise ValueError("side must be either 'ask' or 'bid'.")
        self._plot_candles(axes, side, max_candles)
        axes.set_xlabel("Time")
        axes.set_ylabel("Price")
        axes.set_title(f"{self.currency_pair} - {self.time_span}")
        axes.legend(loc="upper left")

    @pre_plot(nrows=1, ncols=1)
    def plot_ask(
        self,
        axes: plt.Axes = None,
        max_candles: int | None = 2_000,
    ) -> None:
        """Plot the ask series as batched candlesticks."""
        self._plot_candles(axes, "ask", max_candles)

        axes.set_xlabel("Time")
        axes.set_ylabel("Price")
        axes.set_title(f"{self.currency_pair} - {self.time_span}")
        axes.legend(loc="upper left")

    @pre_plot(nrows=1, ncols=1)
    def plot_bid(
        self,
        axes: plt.Axes,
        max_candles: int | None = 2_000,
    ) -> None:
        """
        Plot the bid series as batched candlesticks.

        Parameters
        ----------
        axes : matplotlib.axes.Axes
            Axes to draw on. If None, a new figure+axes are created.
        """
        self._plot_candles(axes, "bid", max_candles)
        axes.set_xlabel("Time")
        axes.set_ylabel("Price")
        axes.set_title(f"{self.currency_pair} - {self.time_span}")
        axes.legend(loc="upper left")

    @pre_plot(nrows=1, ncols=1)
    def plot(
        self,
        axes: plt.Axes,
        max_candles: int | None = 2_000,
    ) -> None:
        """
        Plot both ask and bid series as candlesticks.

        Parameters
        ----------
        axes : matplotlib.axes.Axes
            Axes to draw on. If None, a new figure+axes are created.
        """
        self.plot_ask(axes=axes, max_candles=max_candles, show=False)

        self.plot_bid(axes=axes, max_candles=max_candles, show=False)

        axes.set_xlabel("Time")
        axes.set_ylabel("Price")
        axes.set_title(f"{self.currency_pair} - {self.time_span}")
        axes.legend(loc="upper left")
