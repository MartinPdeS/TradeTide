#include "bollinger_bands.h"


void BollingerBands::process() {
    size_t n = prices->size();
    this->initialize(n);

    for (size_t i = 0; i < n; ++i) {
        this->update_window(i);
        this->compute_bands(i);
        this->detect_signal(i);
    }
}

void BollingerBands::initialize(size_t n) {
    this->sma.assign(n, NAN);
    this->upper_band.assign(n, NAN);
    this->lower_band.assign(n, NAN);
    this->signals.assign(n, 0);
    this->sum = 0.0;
    this->sum_sq = 0.0;
}

void BollingerBands::update_window(size_t idx) {
    double price = (*prices)[idx];
    this->sum += price;
    this->sum_sq += price * price;
    if (idx >= this->window) {
        double old = (*prices)[idx - this->window];
        this->sum    -= old;
        this->sum_sq -= old * old;
    }
}

void BollingerBands::compute_bands(size_t idx) {
    if (idx + 1 >= this->window) {
        double mean = sum / static_cast<double>(this->window);
        double variance = (sum_sq / static_cast<double>(this->window)) - (mean * mean);
        double stddev = std::sqrt(std::max(variance, 0.0));
        this->sma[idx] = mean;
        this->upper_band[idx] = mean + this->multiplier * stddev;
        this->lower_band[idx] = mean - this->multiplier * stddev;
    }
}

void BollingerBands::detect_signal(size_t idx) {
    // only generate when valid bands exist
    if (std::isnan(this->upper_band[idx]) || std::isnan(this->lower_band[idx]))
        return;
    double price = (*this->prices)[idx];
    // buy when price crosses below lower band
    if (idx > 0 && price < this->lower_band[idx] && (*this->prices)[idx-1] >= this->lower_band[idx-1])
        this->signals[idx] = +1;
    // sell when price crosses above upper band
    else if (idx > 0 && price > this->upper_band[idx] && (*this->prices)[idx-1] <= this->upper_band[idx-1])
        this->signals[idx] = -1;
}

