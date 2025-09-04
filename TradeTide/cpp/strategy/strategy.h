#pragma once

#include <vector>
#include <chrono>
#include <memory>
#include "../indicators/base_indicator/base_indicator.h"
#include "../market/market.h"

using Duration = std::chrono::system_clock::duration;
using TimePoint = std::chrono::system_clock::time_point;


class Strategy {
public:
    std::vector<std::shared_ptr<BaseIndicator>> indicators;
    std::vector<int> trade_signals;

    Strategy() = default;

    /**
     * Add an indicator to the strategy.
     * This method allows adding a custom indicator to the strategy for processing market data.
     * @param indicator A shared pointer to the BaseIndicator instance to be added.
     */
    void add_indicator(std::shared_ptr<BaseIndicator> indicator);

    /**
     * Get the trade signal based on the current market data.
     * This method runs all indicators with the provided market data and computes a consensus signal.
     * @param market The market data containing prices to analyze.
     * @return A vector of integers representing the trade signals from each indicator.
     */
    std::vector<int> get_trade_signal(const Market& market);

    /**
     * Detect the region based on the current price.
     * This method should be implemented by derived classes to determine the trading region
     * (e.g., buy, sell, or neutral) based on the current price and indicator logic.
     * @param idx The index of the current price in the prices vector.
     */
    std::vector<int> get_signal_from_indicator(const BaseIndicator& indicator);

    /**
     * Compute the consensus of the columns in the given data.
     * Each column is considered to be in a consensus state if all values are +1 or -1.
     * If a column has mixed values, it is considered neutral (0).
     * @param data A 2D vector representing the data where each inner vector is a column.
     * @return A vector of integers representing the consensus for each column.
     */
    std::vector<int> combine_signals(const std::vector<std::vector<int>>& signals, double threshold = 0.0);

    /**
     * Combine multiple trading signals into a final signal based on weighted scores.
     * Each signal is multiplied by its corresponding weight, and the final score is compared against a threshold.
     * @param signals A 2D vector of signals from different indicators.
     * @param weights A vector of weights corresponding to each indicator's signal.
     * @param threshold A threshold value to determine the final signal.
     * @return A vector of final signals based on the combined scores.
     */
    std::vector<int> combine_signals(const std::vector<std::vector<int>>& signals, const std::vector<double>& weights, double threshold = 0.0);

};
