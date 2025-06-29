#pragma once

#include <vector>
#include <chrono>
#include <string>
#include <iostream>
#include <iomanip>  // for std::setw


#include "../position_collection/position_collection.h"
#include "../strategy/strategy.h"
#include "../exit_strategy/exit_strategy.h"
#include "../market/market.h"
#include "../metrics/metrics.h"
#include "../portfolio/portfolio.h"
#include "../capital_management/capital_management.h"




class ScopedTimer {
public:
    using Clock = std::chrono::high_resolution_clock;

    ScopedTimer(const std::string& name, std::chrono::microseconds& output_duration)
        : label(name), output(output_duration), start(Clock::now()) {}

    ~ScopedTimer() {
        auto end = Clock::now();
        output = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    }

private:
    std::string label;
    std::chrono::microseconds& output;
    Clock::time_point start;
};




class Backtester {
public:
    Strategy strategy;
    ExitStrategy &exit_strategy;
    Market market;
    BaseCapitalManagement &capital_management;
    PositionCollection position_collection;
    Portfolio portfolio;

    // Timers for various phases
    std::chrono::microseconds trade_signal_computation_time;
    std::chrono::microseconds open_time;
    std::chrono::microseconds propagate_time;
    std::chrono::microseconds simulate_time;

    Backtester(
        Strategy& strategy,
        ExitStrategy& exit_strategy,
        Market& market,
        BaseCapitalManagement& capital_management
    ) :
        strategy(strategy),
        exit_strategy(exit_strategy),
        market(market),
        capital_management(capital_management),
        position_collection(market, strategy.get_trade_signal(market), exit_strategy.save_price_data),
        portfolio(position_collection)
    {}

    void run() {
        {
            ScopedTimer timer("Trade Signal Computation", trade_signal_computation_time);
            std::vector<int> trade_signal = strategy.get_trade_signal(market);
        }

        {
            ScopedTimer timer("Opening Positions", open_time);
            position_collection.open_positions(exit_strategy);
        }

        {
            ScopedTimer timer("Propagating Positions", propagate_time);
            position_collection.propagate_positions();
        }

        {
            ScopedTimer timer("Portfolio Simulation", simulate_time);
            portfolio.simulate(capital_management);
        }
    }

    void display() const {
        portfolio.display();
    }

    void print_performance() const {
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
};
