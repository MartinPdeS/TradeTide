from pandas import DataFrame

from dataclasses import dataclass


@dataclass
class SimpleMovingAverage():
    window: int
    min_periods: int

    def apply_to(self, dataframe: DataFrame, column: str) -> DataFrame:
        self.values = dataframe[column].rolling(
            window=self.window,
            min_periods=self.min_periods
        ).mean(engine='numba')

        return self.values

    def add_to_dataframe(self, dataframe, column: str):
        values = self.apply_to(dataframe, column)
        metric_name = self.__repr__()

        dataframe[metric_name] = values

    def plot(self, *args, **kwargs):
        return self.values.plot(*args, **kwargs)

    def __repr__(self) -> str:
        return f"SMA:: window[{self.window}]"

# -
