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

    Backtester(Strategy& strategy, ExitStrategy& exit_strategy, Market& market, BaseCapitalManagement& capital_management, const bool debug_mode);

    void run();

    void display() const;

    void print_performance() const;
};
