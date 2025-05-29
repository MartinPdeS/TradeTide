#pragma once

#include <vector>
#include <chrono>
#include <iostream>
#include <iomanip>

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

    std::vector<TimePoint>* date_list = nullptr;
    std::vector<double>* ask_open_list = nullptr, *bid_open_list = nullptr;
    std::vector<double>* ask_low_list = nullptr, *bid_low_list = nullptr;
    std::vector<double>* ask_high_list = nullptr, *bid_high_list = nullptr;
    std::vector<double>* ask_close_list = nullptr, *bid_close_list = nullptr;

    BasePrice _ask;
    BasePrice _bid;

    void update_time_idx(const size_t time_idx) {
        _ask.date = (*date_list)[time_idx];
        _ask.open = (*open_list)[time_idx];
        _ask.low  = (*low_list)[time_idx];
        _ask.high = (*high_list)[time_idx];
        _ask.close = (*close_list)[time_idx];

        _bid.date = (*date_list)[time_idx];
        _bid.open = (*open_list)[time_idx];
        _bid.low  = (*low_list)[time_idx];
        _bid.high = (*high_list)[time_idx];
        _bid.close = (*close_list)[time_idx];
    }

    /**
     * @brief Initialize the state with a certain capital.
     */
    void initialize(const double capital);

    /**
     * @brief Print a summary of the current state to std::cout.
     */
    void display() const;
};
