from datetime import timedelta

from pydantic.dataclasses import dataclass

from TradeTide.binary.interface_indicators import MACD as NativeMACD
from TradeTide.indicators.base import BaseIndicator
from TradeTide.simulation_settings import SimulationSettings
from TradeTide.utils import config_dict


@dataclass(config=config_dict)
class MACD(NativeMACD, BaseIndicator):
    """Moving Average Convergence Divergence indicator.

    A positive histogram crossover produces a buy signal; a negative crossover
    produces a sell signal.
    """

    fast_window: timedelta = timedelta(minutes=12)
    slow_window: timedelta = timedelta(minutes=26)
    signal_window: timedelta = timedelta(minutes=9)

    def __post_init__(self) -> None:
        unit = SimulationSettings().get_time_unit()
        periods = tuple(
            window / unit
            for window in (self.fast_window, self.slow_window, self.signal_window)
        )
        if any(value < 1 or value != int(value) for value in periods):
            raise ValueError("Each window must contain a whole positive simulation time unit.")
        fast, slow, signal = (int(value) for value in periods)
        if fast >= slow:
            raise ValueError("Require positive windows with fast_window < slow_window.")
        super().__init__(fast_window=fast, slow_window=slow, signal_window=signal)
