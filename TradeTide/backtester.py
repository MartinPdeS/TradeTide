from TradeTide.binary.interface_backtester import BACKTESTER


class Backtester(BACKTESTER):
    """
    Backtester class that extends the BACKTESTER interface for backtesting trading strategies.

    This class provides methods to run backtests, manage capital, and evaluate trading strategies
    using historical market data.
    """

    def __init__(self, strategy, exit_strategy, market, capital_management):
        super().__init__(strategy, exit_strategy, market, capital_management)