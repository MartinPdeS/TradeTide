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
private:
    bool record_enabled = false;

public:
    double equity = 0.0;                          ///< Current portfolio equity
    double capital_at_risk = 0.0;                 ///< Current capital at risk
    size_t number_of_concurrent_positions = 0;    ///< Active positions at current time
    TimePoint time;                               ///< Current timestamp

    std::vector<double> equity_history;
    std::vector<double> capital_at_risk_history;
    std::vector<size_t> concurrent_positions_history;
    std::vector<TimePoint> time_history;

    /**
     * @brief Prepares internal buffers to record state history.
     * @param n_element Expected number of time steps
     */
    void start_record(size_t n_element) {
        this->record_enabled = true;
        this->equity_history.reserve(n_element);
        this->capital_at_risk_history.reserve(n_element);
        this->concurrent_positions_history.reserve(n_element);
        this->time_history.reserve(n_element);
    }

    /**
     * @brief Record all current state metrics to history (if recording is enabled).
     */
    void update() {
        if (!this->record_enabled) return;
        this->equity_history.push_back(this->equity);
        this->capital_at_risk_history.push_back(this->capital_at_risk);
        this->concurrent_positions_history.push_back(this->number_of_concurrent_positions);
        this->time_history.push_back(this->time);
    }

    /**
     * @brief Print a summary of the current state to std::cout.
     */
    void display() const {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Current State:\n";
        std::cout << "--------------\n";
        std::cout << "Equity:                     " << this->equity << "\n";
        std::cout << "Capital at Risk:            " << this->capital_at_risk << "\n";
        std::cout << "Concurrent Open Positions:  " << this->number_of_concurrent_positions << "\n";
        std::time_t t = std::chrono::system_clock::to_time_t(this->time);
        std::cout << "Current Time:               " << std::put_time(std::localtime(&t), "%Y-%m-%d %H:%M:%S") << "\n\n";
    }
};
