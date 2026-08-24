debug_mode = False  # noqa: F401

from .binary import position, capital_management, exit_strategy  # noqa: F401
from .strategy import Strategy  # noqa: F401
from .market import Market  # noqa: F401
from .currencies import Currency  # noqa: F401
from .portfolio import Portfolio  # noqa: F401
from .position_collection import PositionCollection  # noqa: F401
from .backtester import Backtester  # noqa: F401
from .execution import ExecutionCosts, TradeCost  # noqa: F401
from .performance import BacktestResult, PerformanceMetrics, TradeResult  # noqa: F401
from .validation import (  # noqa: F401
    MarketSplit,
    WalkForwardResult,
    WalkForwardSplitter,
    WalkForwardWindow,
    chronological_split,
    slice_market,
)

try:
    from ._version import version as __version__  # noqa: F401

except ImportError:
    __version__ = "0.0.0"

# -
