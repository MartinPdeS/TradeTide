#pragma once

#include <vector>
#include <chrono>
#include <iostream>
#include <iomanip>
#include "../market/market.h"

using TimePoint = std::chrono::system_clock::time_point;


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
    double capital;
    double capital_at_risk = 0.0;                 ///< Current capital at risk
    size_t number_of_concurrent_positions = 0;    ///< Active positions at current time
    TimePoint time;                               ///< Current timestamp
    size_t time_idx;
    size_t position_index;

    BasePrice ask;
    BasePrice bid;

    const Market *market;

    State() = default;


    State(const Market &market, const double capital = 0)
    : market(&market)
    {
        this->initialize(capital);
    }


    void update_time_idx(const size_t time_idx) {
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
