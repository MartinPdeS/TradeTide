#pragma once

#include <vector>
#include <cmath>
#include <cassert>
#include "../../market/market.h"

class BaseIndicator {
public:
    const std::vector<double> *prices;
    std::vector<int> signals, regions;

    BaseIndicator() = default;

    virtual ~BaseIndicator() = default;

    /**
     * Process the indicator.
     * This method should be implemented by derived classes to compute indicators and generate trading signals.
     * It is called after the price data has been set up using `run_with_vector` or `run_with_market`.
     */
    virtual void process() = 0;

    /**
     * Initialize the indicator with the number of price points.
     * This method should be called before processing the prices to set up necessary data structures.
     * @param n The number of price points to initialize for.
     */
    virtual void detect_regions(size_t idx) = 0;

    /**
     * Run the indicator with a vector of prices.
     * This method processes the provided price vector to compute indicators and generate trading signals.
     * @param prices The vector of prices to process.
     * This method assumes that the `prices` member variable is set to point to the provided vector.
     * It processes the prices and generates signals based on the indicator logic.
     * @note This method is typically called after the price data has been loaded and is ready for analysis.
     */
    void run_with_vector(const std::vector<double>& prices);

    /**
     * Run the indicator with market data.
     * This method processes the market's ask prices to compute indicators and generate trading signals.
     * @param market The market data containing prices.
     * This method assumes that the market's ask prices are available in the `ask.close` vector.
     * It processes the prices and generates signals based on the indicator logic.
     * @note The `prices` member variable should be set to point to the market's ask prices.
     * @note This method is typically called after the market data has been loaded and is ready for analysis.
     */
    void run_with_market(const Market& market);

    /**
     * Detect the region based on the current price.
     * This method should be implemented by derived classes to determine the trading region
     * (e.g., buy, sell, or neutral) based on the current price and indicator logic.
     * @param idx The index of the current price in the prices vector.
     */
    void detect_signal_from_region(size_t idx) {
        if (idx == 0) {
            this->signals[idx] = 0;  // no signal on the first index
            return;
        }

        // Step 1: Determine the region at this index
        this->detect_regions(idx);

        // Step 2: Compare with previous region to detect actual signal
        int region_now  = this->regions[idx];
        int region_prev = this->regions[idx - 1];

        // Only set a signal if we're entering a new region
        if (region_now != 0 && region_prev == 0)
            this->signals[idx] = region_now;  // crossing into buy or sell region
        else
            this->signals[idx] = 0;  // no signal on continuation
    }
};