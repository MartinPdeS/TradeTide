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
        ScopedTimer timer("Trade Signal Computation", trade_signal_computation_time);
        std::vector<int> trade_signal = strategy.get_trade_signal(market);
    }{
        ScopedTimer timer("Opening Positions", open_time);
        position_collection.open_positions(exit_strategy);
    }{
        ScopedTimer timer("Propagating Positions", propagate_time);
        position_collection.propagate_positions();
    }{
        ScopedTimer timer("Portfolio Simulation", simulate_time);
        portfolio.simulate(capital_management);
    }
}

void Backtester::display() const {
    portfolio.display();
}

void Backtester::print_performance() const {
    std::cout << "\n--- Backtest Performance Summary ---\n";

    std::cout << std::string(60, '-') << "\n";

    std::cout << std::setw(30) << std::left << "Total Trade Signals: " << this->position_collection.positions.size() << "\n";

    std::cout << std::setw(30) << std::left << "Number of executed positions: " << this->portfolio.executed_positions.size() << "\n\n";

    std::cout << std::setw(30) << std::left << "Step" << std::setw(10) << "Time (microseconds)\n";

    std::cout << std::string(60, '-') << "\n";

    std::cout << std::setw(30) << "Trade Signal Computation" << trade_signal_computation_time.count() << "\n";

    std::cout << std::setw(30) << "Opening Positions" << open_time.count() << "\n";

    std::cout << std::setw(30) << "Propagating Positions" << propagate_time.count() << "\n";

    std::cout << std::setw(30) << "Portfolio Simulation" << simulate_time.count() << "\n";
}
