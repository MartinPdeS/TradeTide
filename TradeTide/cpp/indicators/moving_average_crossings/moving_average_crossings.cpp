#include "moving_average_crossings.h"

MovingAverageCrossing::MovingAverageCrossing(size_t short_window, size_t long_window) : short_window(short_window), long_window(long_window) {
    assert(short_window < long_window && "short_window should be smaller than long_window");
}

void MovingAverageCrossing::process() {
    const size_t n_elements = this->prices->size();

    this->initialize(n_elements);

    for (size_t i = 0; i < n_elements; ++i) {
        this->update_sums(i);
        this->compute_mas(i);
        this->detect_signal(i);
    }
}

void MovingAverageCrossing::initialize(size_t n) {
    this->short_moving_average.assign(n, NAN);
    this->long_moving_average.assign(n,  NAN);
    this->signals.assign(n,  0);
    this->sum_short = 0.0;
    this->sum_long  = 0.0;
}


void MovingAverageCrossing::update_sums(size_t idx) {
    this->sum_short += (*this->prices)[idx];
    if (idx >= short_window)
        this->sum_short -= (*this->prices)[idx - short_window];

    this->sum_long += (*this->prices)[idx];
    if (idx >= long_window)
        this->sum_long -= (*this->prices)[idx - long_window];
}

void MovingAverageCrossing::compute_mas(size_t idx) {
    if (idx + 1 >= short_window)
        this->short_moving_average[idx] = this->sum_short / static_cast<double>(short_window);
    if (idx + 1 >= long_window)
        this->long_moving_average[idx]  = this->sum_long  / static_cast<double>(long_window);
}

void MovingAverageCrossing::detect_signal(size_t idx) {
    // Need at least one prior point and valid MA values
    if (idx == 0)
        return;

    double prev_short = short_moving_average[idx - 1];
    double prev_long  = long_moving_average[idx - 1];
    double curr_short = short_moving_average[idx];
    double curr_long  = long_moving_average[idx];

    if (std::isnan(prev_short) || std::isnan(prev_long) || std::isnan(curr_short) || std::isnan(curr_long))
        return;

    // Golden cross
    if (prev_short <= prev_long && curr_short > curr_long)
        this->signals[idx] = +1;

    // Death cross
    else if (prev_short >= prev_long && curr_short < curr_long)
        this->signals[idx] = -1;

}

