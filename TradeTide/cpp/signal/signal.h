#include <vector>
#include <chrono>
#include <random>
#include <iostream>
#include "../market/market.h"


typedef std::chrono::system_clock::time_point TimePoint;

class Signal {
private:
    std::vector<int> signal_array; // Array of -1 (sell), 0 (hold), +1 (buy)
    TimePoint start_date; // Start date
    TimePoint end_date;   // End date

public:
    // Constructor with Market input
    Signal(const Market& market) : start_date(market.start_date), end_date(market.end_date) {}

    // Generate random signals
    void generate_random();

    // Get signal array
    const std::vector<int>& get_signals() const;

    // Display signals
    void display_signals() const;
};
