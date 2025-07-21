#pragma once

#include <vector>
#include <chrono>
#include <random>
#include <iostream>
#include <fstream>
#include <string>
#include "../market/market.h"

/**
 * @class Signal
 * @brief Encapsulates a time-series trading signal aligned to a market's timeline.
 *
 * The signal vector encodes trade intentions: 1 (long), -1 (short), 0 (neutral).
 * Includes utilities for generation, validation, and export.
 */
class Signal {
    public:
        const Market market;              ///< Market reference with aligned timestamps.
        std::vector<int> trade_signal;    ///< Trade decisions per timestamp: -1 (short), 0 (neutral), 1 (long)

        /**
         * @brief Default constructor for uninitialized signal.
         */
        Signal() = default;

        /**
         * @brief Construct signal aligned with given market.
         * @param market Market object providing timeline and metadata.
         */
        explicit Signal(const Market& market);

        /**
         * @brief Generate random long/short/neutral signals.
         * @param probability Probability of a non-zero signal at each time.
         */
        void generate_random(const double probability);

        /**
         * @brief Generate only long (1 or 0) signals randomly.
         * @param probability Probability of assigning a long position.
         */
        void generate_only_long(const double probability);

        /**
         * @brief Generate only short (-1 or 0) signals randomly.
         * @param probability Probability of assigning a short position.
         */
        void generate_only_short(const double probability);

        /**
         * @brief Get the internal signal vector.
         * @return const reference to signal vector.
         */
        const std::vector<int>& get_signals() const;

        /**
         * @brief Print signal values with timestamps for visual inspection.
         * @param max_count Maximum number of entries to display.
         */
        void display(size_t max_count = 20) const;

        /**
         * @brief Export signal to a CSV file.
         * @param filepath Path to output file.
         */
        void to_csv(const std::string& filepath) const;

        /**
         * @brief Count the number of long and short entries.
         * @return Pair (long_count, short_count)
         */
        std::pair<size_t, size_t> count_signals() const;

        /**
         * @brief Check if signal vector matches length of market.
         * @return True if size matches market timestamps.
         */
        bool validate_against_market() const;

        /**
         * @brief Placeholder hook for rule-based signal logic.
         * @return Current trade signal vector.
         */
        std::vector<int> compute_trade_signal();
};