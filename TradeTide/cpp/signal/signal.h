#pragma once

#include <vector>
#include <chrono>
#include <random>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <string>
#include "../market/market.h"

/**
 * @brief Represents a trading signal time series linked to a Market.
 *
 * A signal is a vector of integers (typically -1, 0, +1) representing short, no trade, or long entries.
 * Provides utilities to generate, inspect, and validate signal sequences.
 */
class Signal {
    public:
        const Market market;              ///< Market data context
        std::vector<int> trade_signal;    ///< Signal values (-1 = short, 0 = no trade, 1 = long)

        /**
         * @brief Default constructor.
         */
        Signal() = default;

        /**
         * @brief Constructs a Signal linked to a Market.
         * @param market Market data reference
         */
        Signal(const Market& market) : market(market) {
            this->trade_signal.resize(market.dates.size(), 0);
        }

        /**
         * @brief Randomly generate entry signals over the time series.
         * @param probability Probability of signal being non-zero at any given index
         */
        void generate_random(double probability);

        /**
         * @brief Access the internal signal vector.
         */
        const std::vector<int>& get_signals() const;

        /**
         * @brief Display the first N signals with timestamps.
         */
        void display(size_t max_count = 20) const;

        /**
         * @brief Save the signal to a CSV file.
         * @param filepath Destination path
         */
        void to_csv(const std::string& filepath) const;

        /**
         * @brief Count the number of long and short entries.
         * @return std::pair<long_count, short_count>
         */
        std::pair<size_t, size_t> count_signals() const;

        /**
         * @brief Validate that the signal vector size matches market length.
         * @return true if valid
         */
        bool validate_against_market() const;

        /**
         * @brief Placeholder for a signal logic engine or rule-based generator.
         * @return vector of trade signals
         */
        std::vector<int> compute_trade_signal();

};
