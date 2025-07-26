from TradeTide.binary.interface_backtester import BACKTESTER
from TradeTide.market import Market
from TradeTide.strategy import Strategy
import matplotlib.pyplot as plt
import numpy as np
from MPSPlots.styles import mps as plot_style


class Backtester(BACKTESTER):
    """
    Backtester class that extends the BACKTESTER interface for backtesting trading strategies.

    This class provides methods to run backtests, manage capital, and evaluate trading strategies
    using historical market data.
    """

    def __init__(self, strategy: Strategy, exit_strategy, market: Market, capital_management):
        super().__init__(
            strategy=strategy,
            exit_strategy=exit_strategy,
            market=market,
            capital_management=capital_management
        )

        self.strategy = strategy
        self.exit_strategy = exit_strategy
        self.market = market
        self.capital_management = capital_management

    def plot(self, *plot_types, show: bool = True, figsize: tuple = (14, 10)) -> plt.Figure:
        """
        Create comprehensive visualization of backtesting results.

        Parameters
        ----------
        *plot_types : str
            Types of plots to include. Options: 'strategy', 'equity', 'positions', 'drawdown', 'trades'.
            If no arguments provided, shows all plot types.
        show : bool, optional
            Whether to display the plot immediately, by default True
        figsize : tuple, optional
            Figure size in inches, by default (14, 10)

        Returns
        -------
        matplotlib.figure.Figure
            The figure object containing all plots

        Examples
        --------
        >>> backtester.plot()  # All plots
        >>> backtester.plot('strategy', 'equity')  # Specific plots only
        >>> backtester.plot('equity', show=False)  # Don't show immediately
        """
        # Default to all plot types if none specified
        if len(plot_types) == 0:
            plot_types = ('strategy', 'equity', 'positions', 'drawdown')
        elif len(plot_types) == 1 and isinstance(plot_types[0], (tuple, list)):
            plot_types = plot_types[0]

        # Validate plot types
        valid_types = {'strategy', 'equity', 'positions', 'drawdown', 'trades'}
        plot_types = [pt for pt in plot_types if pt in valid_types]

        if not plot_types:
            raise ValueError(f"No valid plot types provided. Valid options: {valid_types}")

        n_plots = len(plot_types)

        with plt.style.context(plot_style):
            fig, axes = plt.subplots(nrows=n_plots, ncols=1, figsize=figsize, sharex=True)

            # Handle single subplot case
            if n_plots == 1:
                axes = [axes]

            plot_methods = {
                'strategy': self._plot_strategy,
                'equity': self._plot_equity,
                'positions': self._plot_positions,
                'drawdown': self._plot_drawdown,
                'trades': self._plot_trades
            }

            for ax, plot_type in zip(axes, plot_types):
                plot_methods[plot_type](ax)

            # Set common x-axis label on bottom plot
            axes[-1].set_xlabel('Time')

            # Add main title
            fig.suptitle('Backtesting Results Overview', fontsize=16, fontweight='bold', y=0.98)

            plt.tight_layout()
            plt.subplots_adjust(top=0.93)

            if show:
                plt.show()

        return fig

    def _plot_strategy(self, ax: plt.Axes) -> None:
        """Plot market prices with strategy signals and indicators."""
        # Plot market data
        self.market.plot(ax=ax, show_ask=True, show_bid=False, show=False)

        # Get strategy signals
        trade_signals = self.strategy.get_trade_signal(self.market)

        # Plot buy/sell signals
        buy_signals = np.where(np.array(trade_signals) == 1)[0]
        sell_signals = np.where(np.array(trade_signals) == -1)[0]

        if len(buy_signals) > 0:
            ax.scatter(
                [self.market.dates[i] for i in buy_signals],
                [self.market.ask.close[i] for i in buy_signals],
                color='green', marker='^', s=60, label='Buy Signal', zorder=5
            )

        if len(sell_signals) > 0:
            ax.scatter(
                [self.market.dates[i] for i in sell_signals],
                [self.market.ask.close[i] for i in sell_signals],
                color='red', marker='v', s=60, label='Sell Signal', zorder=5
            )

        # Add indicators if available
        if hasattr(self.strategy, 'indicators') and self.strategy.indicators:
            for indicator in self.strategy.indicators:
                if hasattr(indicator, 'plot'):
                    indicator.plot(ax, show_metric=True)

        ax.set_ylabel('Price')
        ax.set_title('Trading Strategy Overview')
        ax.legend(loc='upper left')

    def _plot_equity(self, ax: plt.Axes) -> None:
        """Plot portfolio equity curve over time."""
        if hasattr(self, '_cpp_portfolio') and self._cpp_portfolio is not None:
            equity_data = self._cpp_portfolio.record.equity
            time_data = self._cpp_portfolio.record.time
            initial_capital = self._cpp_portfolio.record.initial_capital

            ax.plot(time_data, equity_data, color='blue', linewidth=2, label='Portfolio Equity')
            ax.axhline(initial_capital, color='red', linestyle='--', linewidth=1, alpha=0.7, label='Initial Capital')

            # Calculate and show final return
            final_return = (equity_data[-1] - initial_capital) / initial_capital * 100
            ax.text(0.02, 0.98, f'Total Return: {final_return:.2f}%', transform=ax.transAxes, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        else:
            ax.text(0.5, 0.5, 'Portfolio data not available.\nRun backtest first.', transform=ax.transAxes, ha='center', va='center')

        ax.set_ylabel('Equity ($)')
        ax.set_title('Portfolio Equity Curve')
        ax.legend()

    def _plot_positions(self, ax: plt.Axes) -> None:
        """Plot number of open positions over time."""
        if hasattr(self, '_cpp_portfolio') and self._cpp_portfolio is not None:
            positions_data = self._cpp_portfolio.record.concurrent_positions
            time_data = self._cpp_portfolio.record.time

            ax.step(time_data, positions_data, where='mid', color='orange', linewidth=2, label='Open Positions')
            ax.fill_between(time_data, 0, positions_data, step='mid', color='orange', alpha=0.3)

            # Show max concurrent positions
            max_positions = max(positions_data) if positions_data else 0
            ax.text(0.02, 0.98,
                f'Max Concurrent: {max_positions}',
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
            )
        else:
            ax.text(0.5, 0.5, 'Portfolio data not available.\nRun backtest first.', transform=ax.transAxes, ha='center', va='center')

        ax.set_ylabel('# Positions')
        ax.set_title('Open Positions Over Time')
        ax.legend()

    def _plot_drawdown(self, ax: plt.Axes) -> None:
        """Plot portfolio drawdown over time."""
        if hasattr(self, '_cpp_portfolio') and self._cpp_portfolio is not None:
            equity_data = np.array(self._cpp_portfolio.record.equity)
            time_data = self._cpp_portfolio.record.time

            # Calculate running maximum (peak)
            running_max = np.maximum.accumulate(equity_data)

            # Calculate drawdown as percentage
            drawdown = (equity_data - running_max) / running_max * 100

            ax.fill_between(time_data, 0, drawdown, color='red', alpha=0.3, label='Drawdown')
            ax.plot(time_data, drawdown, color='red', linewidth=1)

            # Show maximum drawdown
            max_drawdown = min(drawdown)
            ax.text(0.02, 0.02,
                f'Max Drawdown: {max_drawdown:.2f}%',
                transform=ax.transAxes,
                verticalalignment='bottom',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
            )
        else:
            ax.text(0.5, 0.5, 'Portfolio data not available.\nRun backtest first.', transform=ax.transAxes, ha='center', va='center')

        ax.set_ylabel('Drawdown (%)')
        ax.set_title('Portfolio Drawdown')
        ax.legend()

    def _plot_trades(self, ax: plt.Axes) -> None:
        """Plot trade distribution and statistics."""
        if hasattr(self, 'portfolio') and self.portfolio is not None:
            ax.text(0.5, 0.5, 'Trade analysis plot\n(Implementation depends on\navailable trade data)', transform=ax.transAxes, ha='center', va='center')
        else:
            ax.text(0.5, 0.5, 'Portfolio data not available.\nRun backtest first.', transform=ax.transAxes, ha='center', va='center')

        ax.set_ylabel('Trade P&L')
        ax.set_title('Trade Distribution')

    def plot_summary(self, show: bool = True, figsize: tuple = (16, 12)) -> plt.Figure:
        """
        Create a comprehensive summary dashboard of backtesting results.

        Parameters
        ----------
        show : bool, optional
            Whether to display the plot immediately, by default True
        figsize : tuple, optional
            Figure size in inches, by default (16, 12)

        Returns
        -------
        matplotlib.figure.Figure
            The figure object containing the summary dashboard
        """
        with plt.style.context(plot_style):
            fig = plt.figure(figsize=figsize)

            # Create a 3x2 grid layout
            gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

            # Strategy overview (top, full width)
            ax1 = fig.add_subplot(gs[0, :])
            self._plot_strategy(ax1)

            # Equity curve (middle left)
            ax2 = fig.add_subplot(gs[1, 0])
            self._plot_equity(ax2)

            # Drawdown (middle right)
            ax3 = fig.add_subplot(gs[1, 1])
            self._plot_drawdown(ax3)

            # Positions (bottom left)
            ax4 = fig.add_subplot(gs[2, 0])
            self._plot_positions(ax4)

            # Performance metrics (bottom right)
            ax5 = fig.add_subplot(gs[2, 1])
            self._plot_performance_metrics(ax5)

            fig.suptitle('Backtesting Summary Dashboard', fontsize=18, fontweight='bold', y=0.98)

            if show:
                plt.show()

        return fig

    def _plot_performance_metrics(self, ax: plt.Axes) -> None:
        """Display key performance metrics as text."""
        ax.axis('off')  # Hide axes for text display

        if hasattr(self, '_cpp_portfolio') and self._cpp_portfolio is not None:
            # Calculate key metrics
            equity_data = np.array(self._cpp_portfolio.record.equity)
            initial_capital = self._cpp_portfolio.record.initial_capital

            total_return = (equity_data[-1] - initial_capital) / initial_capital * 100

            # Calculate Sharpe ratio (simplified)
            returns = np.diff(equity_data) / equity_data[:-1]
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0

            # Calculate max drawdown
            running_max = np.maximum.accumulate(equity_data)
            drawdown = (equity_data - running_max) / running_max * 100
            max_drawdown = min(drawdown)

            # Calculate win rate (placeholder)
            win_rate = 0.0  # Would need individual trade data

            metrics_text = f"""
Performance Metrics

Total Return: {total_return:.2f}%
Sharpe Ratio: {sharpe_ratio:.2f}
Max Drawdown: {max_drawdown:.2f}%
Win Rate: {win_rate:.1f}%

Initial Capital: ${initial_capital:,.0f}
Final Equity: ${equity_data[-1]:,.0f}
"""
        else:
            metrics_text = """
Performance Metrics

No data available.
Run backtest first.
"""

        ax.text(0.1, 0.9, metrics_text, transform=ax.transAxes, fontsize=12,
               verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))

        ax.set_title('Key Performance Indicators')

