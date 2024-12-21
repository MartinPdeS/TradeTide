#pragma once

#include <vector>
#include <random>
#include <ctime>
#include <iostream>
#include <algorithm>

class Market {
private:
    std::vector<double> open_prices;
    std::vector<double> close_prices;
    std::vector<double> high_prices;
    std::vector<double> low_prices;

public:
    std::time_t start_date;
    std::time_t end_date;

public:
    // Constructor for predefined data
    Market(std::time_t start_date, std::time_t end_date,
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
    Market(std::time_t start_date, std::time_t end_date)
        : start_date(start_date), end_date(end_date) {
        generate_random_market_data();
    }

    // Generate random market data
    void generate_random_market_data() {
        // Calculate the number of days between start_date and end_date
        int days = static_cast<int>(std::difftime(end_date, start_date) / (60 * 60 * 24));
        if (days <= 0) {
            std::cerr << "Invalid date range provided.\n";
            return;
        }

        // Initialize random number generator
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<> dist_price(1.0, 100.0); // Generate prices between $1 and $100
        std::uniform_real_distribution<> dist_volatility(0.01, 5.0); // Generate daily price range percentage

        open_prices.clear();
        close_prices.clear();
        high_prices.clear();
        low_prices.clear();

        double prev_close = dist_price(gen); // Start with a random price

        for (int i = 0; i <= days; ++i) {
            double open = prev_close;
            double volatility = dist_volatility(gen) / 100.0;
            double high = open * (1 + volatility);
            double low = open * (1 - volatility);
            double close = low + (high - low) * dist_volatility(gen) / 100.0;

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