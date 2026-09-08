#include "backtester.h"




Backtester::Backtester(Strategy& strategy, ExitStrategy& exit_strategy, Market& market, BaseCapitalManagement& capital_management, const bool debug_mode) :
    strategy(strategy),
    exit_strategy(exit_strategy),
    market(market),
    capital_management(capital_management),
    position_collection(market, strategy.get_trade_signal(market), exit_strategy.save_price_data),
    portfolio(position_collection)
{
    position_collection.debug_mode = debug_mode;
    portfolio.debug_mode = debug_mode;
}

void Backtester::run() {
    {
        ScopedTimer timer("Trade Signal Computation", trade_signal_computation_run_time);
        std::vector<int> trade_signal = strategy.get_trade_signal(market);
    }{
        ScopedTimer timer("Opening Positions", open_position_run_time);
        position_collection.open_positions(exit_strategy);
    }{
        ScopedTimer timer("Propagating Positions", propagate_run_time);
        position_collection.propagate_positions();
    }{
        ScopedTimer timer("Portfolio Run Time", portfolio_run_time);
        portfolio.simulate(capital_management);
    }
}

void Backtester::display() const {
    portfolio.display();
}

void Backtester::print_performance() {
    // Section: Performance metrics (if available)
    Metrics m = portfolio.get_metrics();

    this->print_section("Performance Metrics");
    this->print_line("Total Return:", std::to_string(m.total_return) + " %");
    this->print_line("Annualized Return:", std::to_string(m.annualized_return) + " %");
    this->print_line("Volatility:", std::to_string(m.volatility * 100) + " %");
    this->print_line("Sharpe Ratio:", std::to_string(m.sharpe_ratio));
    this->print_line("Sortino Ratio:", std::to_string(m.sortino_ratio));
    this->print_line("Max Drawdown:", std::to_string(m.max_drawdown) + " %");
    this->print_line("Win Rate:", std::to_string(m.win_loss_ratio * 100) + " %");
}


void Backtester::print_run_times() const {
    this->print_section("Execution Time (µs)");
    this->print_line("Trade Signal Computation:", std::to_string(trade_signal_computation_run_time.count()));
    this->print_line("Opening Positions:", std::to_string(open_position_run_time.count()));
    this->print_line("Propagating Positions:", std::to_string(propagate_run_time.count()));
    this->print_line("Portfolio Simulation Runtime:", std::to_string(portfolio_run_time.count()));
}

void Backtester::print_basic_info() const {
    this->print_section("Capital & Trades");
    this->print_line("Total Trade Signals:", std::to_string(position_collection.positions.size()));
    this->print_line("Executed Positions:", std::to_string(portfolio.executed_positions.size()));
    this->print_line("Total Simulation Steps:", std::to_string(market.dates.size()));
}


void Backtester::print_summary() {
    // Header
    this->print_header("Backtesting Performance Summary");

    if (this->portfolio.executed_positions.empty()) {
        std::cout << "No data available. Run backtest first.\n";
        std::cout << std::string(60, '=') << "\n\n";
        return;
    }

    // Section: Basic info
    this->print_basic_info();

    // Section: Timing
    this->print_run_times();

    // Section: Performance metrics
    this->print_performance();

    // Footer
    std::cout << std::string(60, '=') << "\n\n";
}
