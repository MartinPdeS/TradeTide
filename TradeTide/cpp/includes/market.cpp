#pragma once

#include <vector>
#include <random>
#include <chrono>
#include <iostream>

class Market {
private:
    std::vector<double> open_prices;
    std::vector<double> close_prices;
    std::vector<double> high_prices;
    std::vector<double> low_prices;

public:
    std::chrono::system_clock::time_point start_date;
    std::chrono::system_clock::time_point end_date;

    // Constructor for predefined data
    Market(const std::chrono::system_clock::time_point start_date,
           const std::chrono::system_clock::time_point end_date,
           const std::vector<double>& input_open,
           const std::vector<double>& input_close,
           const std::vector<double>& input_high,
           const std::vector<double>& input_low)
        : start_date(start_date), end_date(end_date),
          open_prices(input_open), close_prices(input_close),
          high_prices(input_high), low_prices(input_low) {
        if (input_open.empty() || input_close.empty() || input_high.empty() || input_low.empty()) {
            std::cerr << "Error: Input arrays must not be empty.\n";
        }
    }

    // Constructor for random data generation
    Market(const std::chrono::system_clock::time_point start_date,
           const std::chrono::system_clock::time_point end_date)
        : start_date(start_date), end_date(end_date) {
        generate_random_market_data();
    }

    void generate_random_market_data() {
        // Calculate the number of days between start_date and end_date
        auto duration = std::chrono::duration_cast<std::chrono::days>(end_date - start_date).count();
        if (duration <= 0) {
            std::cerr << "Invalid date range provided.\n";
            return;
        }

        // Initialize random number generator
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<> dist_price(1.0, 100.0); // Prices between $1 and $100
        std::uniform_real_distribution<> dist_volatility(0.01, 0.05); // Daily volatility between 1% and 5%

        open_prices.clear();
        close_prices.clear();
        high_prices.clear();
        low_prices.clear();

        double prev_close = dist_price(gen); // Start with a random price

        for (int i = 0; i <= duration; ++i) {
            double open = prev_close;
            double volatility = dist_volatility(gen);
            double high = open * (1 + volatility);
            double low = open * (1 - volatility);
            double close = low + (high - low) * dist_volatility(gen);

            open_prices.push_back(open);
            close_prices.push_back(close);
            high_prices.push_back(high);
            low_prices.push_back(low);

            prev_close = close;
        }
    }

    // Getters for market data
    const std::vector<double>& get_open_prices() const { return open_prices; }
    const std::vector<double>& get_close_prices() const { return close_prices; }
    const std::vector<double>& get_high_prices() const { return high_prices; }
    const std::vector<double>& get_low_prices() const { return low_prices; }

    // Display market data
    void display_market_data() const {
        std::cout << "Market Data:\n";
        for (size_t i = 0; i < open_prices.size(); ++i) {
            std::cout << "Day " << i + 1 << ": "
                      << "Open: " << open_prices[i] << ", "
                      << "High: " << high_prices[i] << ", "
                      << "Low: " << low_prices[i] << ", "
                      << "Close: " << close_prices[i] << "\n";
        }
    }
};