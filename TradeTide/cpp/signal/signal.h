#pragma once

#include <vector>
#include <chrono>
#include <random>
#include <iostream>
#include "../market/market.h"


class Signal {
public:
    const Market &market;
    std::vector<int> trade_signal;

    // Constructor with Market input
    Signal(const Market& market) : market(market) {}

    // Generate random signals
    void generate_random(const double probability);

    // Get signal array
    const std::vector<int>& get_signals() const;

    // Display signals
    void display_signal() const;

    std::vector<int> compute_trade_signal();
};
