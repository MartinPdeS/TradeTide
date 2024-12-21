#pragma once

#include <vector>
#include <random>
#include <ctime>
#include <iostream>

#pragma once

#include <vector>
#include <random>
#include <ctime>
#include <iostream>
#include "market.cpp"

class Signal {
private:
    std::vector<int> signal_array; // Array of -1 (sell), 0 (nothing), +1 (buy)
    std::time_t start_date;        // Start date of the data array
    std::time_t end_date;          // End date of the data array

public:
    // Constructor with Market input
    Signal(const Market& market)
        : start_date(market.start_date), end_date(market.end_date) {
    }


    // Generate random signals
    void generate_random() {
        // Calculate the number of days between start_date and end_date
        int days = static_cast<int>(std::difftime(end_date, start_date) / (60 * 60 * 24));
        if (days <= 0) {
            std::cerr << "Invalid date range provided.\n";
            return;
        }

        // Initialize random number generator
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dist(-1, 1); // Generate values -1, 0, or +1

        signal_array.clear();
        for (int i = 0; i <= days; ++i) {
            signal_array.push_back(dist(gen));
        }
    }

    // Get signal array
    const std::vector<int>& get_signals() const {
        return signal_array;
    }

    // Display signals
    void display_signals() const {
        std::cout << "Signals:\n";
        for (size_t i = 0; i < signal_array.size(); ++i) {
            std::cout << "Day " << i + 1 << ": " << signal_array[i] << "\n";
        }
    }
};
