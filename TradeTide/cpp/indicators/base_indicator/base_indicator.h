#pragma once

#include <vector>
#include <cmath>
#include <cassert>
#include "../../market/market.h"

class BaseIndicator {
public:
    const std::vector<double> *prices;
    std::vector<int> signals;

    BaseIndicator() = default;

    virtual ~BaseIndicator() = default;

    /**
     * Process the indicator.
     * This method should be implemented by derived classes to compute indicators and generate trading signals.
     * It is called after the price data has been set up using `run_with_vector` or `run_with_market`.
     */
    virtual void process() = 0;

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
};