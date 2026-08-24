from datetime import timedelta

from pydantic.dataclasses import dataclass

from TradeTide.binary.interface_indicators import RELATIVESTRENGTHINDEX
from TradeTide.indicators.base import BaseIndicator
from TradeTide.simulation_settings import SimulationSettings
from TradeTide.utils import config_dict


@dataclass(config=config_dict)
class RelativeStrengthIndex(RELATIVESTRENGTHINDEX, BaseIndicator):
    """Relative Strength Index (RSI) with overbought/oversold trade regions."""

    window: timedelta
    over_bought: float = 70.0
    over_sold: float = 30.0

    def __post_init__(self) -> None:
        periods = self.window / SimulationSettings().get_time_unit()
        if periods < 1 or periods != int(periods):
            raise ValueError("window must be at least one whole simulation time unit.")
        if not 0 <= self.over_sold < self.over_bought <= 100:
            raise ValueError("Require 0 <= over_sold < over_bought <= 100.")
        super().__init__(
            window=int(periods),
            over_bought=self.over_bought,
            over_sold=self.over_sold,
        )
