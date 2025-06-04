#pragma once

#include <vector>
#include <chrono>

using TimePoint = std::chrono::system_clock::time_point;

#include "../state/state.h"


/**
 * @brief Tracks portfolio state over time including equity, risk, and position count.
 */
class Record {
    private:
        bool record_enabled = false;

    public:
        State* state;
        std::vector<double> equity;
        std::vector<double> capital;
        std::vector<double> capital_at_risk;
        std::vector<size_t> concurrent_positions;
        std::vector<TimePoint> time;
        double initial_capital = 0.0;                ///< Initial capital at the start of the simulation

        /**
         * @brief Prepares internal buffers to record state history.
         * @param n_element Expected number of time steps
         */
        void start_record(size_t n_element);

        /**
         * @brief Record all current state metrics to history (if recording is enabled).
         */
        void update();
};