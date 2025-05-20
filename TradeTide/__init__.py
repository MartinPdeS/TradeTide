from .binary import capital_management, exit_strategy, position
# from .strategy import *
# from TradeTide import indicators

try:
    from ._version import version as __version__  # noqa: F401

except ImportError:
    __version__ = "0.0.0"

# -
