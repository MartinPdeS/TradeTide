#pragma once

#include <vector>
#include <chrono>
#include <iostream>
#include <iomanip>

using TimePoint = std::chrono::system_clock::time_point;

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

     /**
     * @brief Initialize the state with a certain capital.
     */
    void initialize(const double capital);

    /**
     * @brief Print a summary of the current state to std::cout.
     */
    void display() const;
};
