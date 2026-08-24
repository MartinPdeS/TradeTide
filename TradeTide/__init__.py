debug_mode = False  # noqa: F401

from .binary import position, capital_management, exit_strategy  # noqa: F401
from .strategy import Strategy  # noqa: F401
from .binary.interface_market import Market  # noqa: F401
from .market_plotting import plot_market, plot_market_candles  # noqa: F401
from .currencies import Currency  # noqa: F401
from .portfolio import Portfolio  # noqa: F401
from .position_collection import PositionCollection  # noqa: F401
from .backtester import Backtester  # noqa: F401
from .execution import ExecutionCosts, TradeCost  # noqa: F401
from .performance import BacktestResult, PerformanceMetrics, TradeResult  # noqa: F401
from .performance import plot_equity_drawdown  # noqa: F401
from .debug import (  # noqa: F401
    configure_logging,
    disable_debug_logging,
    enable_debug_logging,
)
from .validation import (  # noqa: F401
    MarketSplit,
    WalkForwardResult,
    WalkForwardSplitter,
    WalkForwardWindow,
    chronological_split,
    slice_market,
)
from .data_quality import (  # noqa: F401
    DataQualityIssue,
    DataQualityReport,
    IssueSeverity,
    validate_market_data,
)
from .ledger import LedgerEntry, PositionAnalytics, TradeLedger  # noqa: F401
from .orders import Order, OrderBook, OrderFill, OrderSide, OrderStatus, OrderType  # noqa: F401

try:
    from ._version import version as __version__  # noqa: F401

except ImportError:
    __version__ = "0.0.0"

# -
