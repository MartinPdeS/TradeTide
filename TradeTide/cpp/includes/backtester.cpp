#pragma once

#include <vector>
#include <string>
#include <iostream>
#include "portfolio.cpp"

class Backtester {
private:
    Portfolio& portfolio; // Reference to a Portfolio instance
    std::vector<std::tuple<std::string, bool, double, double>> signals; // {currency_pair, is_long, entry_price, pip_value}

public:
    // Constructor
    Backtester(Portfolio& portfolio, const std::vector<std::tuple<std::string, bool, double, double>>& input_signals)
        : portfolio(portfolio), signals(input_signals) {}

    // Run the backtest
    void run() {
        std::cout << "Running backtest...\n";
        for (const auto& signal : signals) {
            const std::string& currency_pair = std::get<0>(signal);
            bool is_long = std::get<1>(signal);
            double entry_price = std::get<2>(signal);
            double pip_value = std::get<3>(signal);

            if (portfolio.add_position(currency_pair, is_long, entry_price, pip_value)) {
                std::cout << "Executed trade: "
                          << (is_long ? "Buy" : "Sell") << " "
                          << currency_pair << " at price " << entry_price << "\n";
            } else {
                std::cout << "Trade failed for " << currency_pair << " at price " << entry_price << "\n";
            }
        }

        // Display results
        std::cout << "\nBacktest complete.\n";
        portfolio.display_positions();
        portfolio.print_metrics(2.0); // Assuming a 2% risk-free rate
    }
};