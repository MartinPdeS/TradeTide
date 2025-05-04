#pragma once

#include <vector>
#include <string>
#include <iostream>
#include "../portfolio/portfolio.h"

class Backtester {
private:
    Portfolio portfolio; // Reference to a Portfolio instance
    std::vector<std::tuple<std::string, bool, double, double>> signals; // {currency_pair, is_long, entry_price, pip_value}

public:
    // Constructor
    Backtester() = default;

    Backtester(Portfolio& portfolio, const std::vector<std::tuple<std::string, bool, double, double>>& input_signals)
        : portfolio(portfolio), signals(input_signals) {}

    // Run the backtest
    void run();
};