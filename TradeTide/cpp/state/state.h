#pragma once

#include <vector>
#include <chrono>
#include <iostream>
#include <iomanip>
#include "../market/market.h"

using TimePoint = std::chrono::system_clock::time_point;

/**
 * @brief Represents a base price structure with open, low, high, and close prices.
 *
 * This class is used to store the price data for both ask and bid prices in the market.
 */
class BasePrice {
public:
    double open = 0.0, low = 0.0, high = 0.0, close = 0.0;
};



/**
 * @brief Tracks portfolio state over time including equity, risk, and position count.
 */
class State {
public:
    double equity = 0.0;                          ///< Current portfolio equity
    double capital;                               ///< Initial capital
    double capital_at_risk = 0.0;                 ///< Current capital at risk
    size_t number_of_concurrent_positions = 0;    ///< Active positions at current time
    TimePoint current_date;                       ///< Current timestamp
    size_t time_idx;                              ///< Index in the market data for current time
    size_t position_index;                        ///< Index of the current position
    size_t n_elements;                            ///< Total number of elements in the market data

    BasePrice ask, bid, *closing_price, *opening_price; ///< Current ask and bid prices

    const std::vector<double> *closing_prices; ///< Closing prices for the current state
    const std::vector<TimePoint> *dates; ///< Opening prices for the current state
    const Market *market; ///< Reference to the market data

    State() = default; // Default constructor for State

    /**
     * @brief Constructs a new State object.
     *
     * @param market Reference to the Market object containing market data.
     * @param capital Initial capital for the portfolio.
     */
    State(const Market &market, double capital = 0);

    /**
     * @brief Display the current state information.
     */
    void display();

    /**
     * @brief Update the state with a new time index.
     *
     * @param time_idx Index of the market data to update the state with.
     */
    void update_time_idx(const size_t time_idx);

    /**
     * @brief Initialize the state with a certain capital.
     */
    void initialize(const double capital = 0);

    /**
     * @brief Print a summary of the current state to std::cout.
     */
    void display() const;
};
