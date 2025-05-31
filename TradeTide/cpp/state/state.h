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
    TimePoint date;

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
    TimePoint time;                               ///< Current timestamp
    size_t time_idx;                              ///< Index in the market data for current time
    size_t position_index;                        ///< Index of the current position
    size_t n_elements;                            ///< Total number of elements in the market data

    BasePrice ask, bid, *close_price, *open_price; ///< Current ask and bid prices

    const Market *market; ///< Reference to the market data

    State() = default; // Default constructor for State

    /**
     * @brief Constructs a new State object.
     *
     * @param market Reference to the Market object containing market data.
     * @param capital Initial capital for the portfolio.
     */
    State(const Market &market, const double capital = 0): market(&market)
    {
        this->n_elements = market.dates.size();
        this->initialize(capital);
    }

    /**
     * @brief Display the current state information.
     */
    void display() {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Time: " << std::chrono::system_clock::to_time_t(time) << "\n";
        std::cout << "Time idx: " << time_idx << "\n";
        std::cout << "Equity: " << equity << "\n";
        std::cout << "Capital at Risk: " << capital_at_risk << "\n";
        std::cout << "Number of Concurrent Positions: " << number_of_concurrent_positions << "\n";
        std::cout << "Ask Price - Open: " << ask.open << ", Low: " << ask.low << ", High: " << ask.high << ", Close: " << ask.close << "\n";
        std::cout << "Bid Price - Open: " << bid.open << ", Low: " << bid.low << ", High: " << bid.high << ", Close: " << bid.close << "\n";
    }

    /**
     * @brief Update the state with a new time index.
     *
     * @param time_idx Index of the market data to update the state with.
     */
    void update_time_idx(const size_t time_idx) {
        this->time_idx = time_idx;
        time = this->market->dates[time_idx];

        ask.open = this->market->ask.open[time_idx];
        ask.low  = this->market->ask.low[time_idx];
        ask.high = this->market->ask.high[time_idx];
        ask.close = this->market->ask.close[time_idx];

        bid.open = this->market->bid.open[time_idx];
        bid.low  = this->market->bid.low[time_idx];
        bid.high = this->market->bid.high[time_idx];
        bid.close = this->market->bid.close[time_idx];
    }

    /**
     * @brief Initialize the state with a certain capital.
     */
    void initialize(const double capital = 0);

    /**
     * @brief Print a summary of the current state to std::cout.
     */
    void display() const;
};
