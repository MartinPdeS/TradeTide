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
        this->detect_signal_from_region(i);
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

void MovingAverageCrossing::detect_regions(size_t idx) {
    if (idx == 0)
        return;

    double short_ma = short_moving_average[idx];
    double long_ma  = long_moving_average[idx];

    if (std::isnan(short_ma) || std::isnan(long_ma)) {
        this->regions[idx] = 0;
        return;
    }

    // Bullish region (short > long)
    if (short_ma > long_ma)
        this->regions[idx] = +1;
    // Bearish region (short < long)
    else if (short_ma < long_ma)
        this->regions[idx] = -1;
    else
        this->regions[idx] = 0;
}


