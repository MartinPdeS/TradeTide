#include "bollinger_bands.h"


void BollingerBands::process() {
    size_t n_elements = prices->size();
    this->initialize(n_elements);

    for (size_t i = 0; i < n_elements; ++i) {
        this->update_window(i);
        this->compute_bands(i);
        this->detect_regions(i);
    }
}

void BollingerBands::initialize(size_t n_elements) {
    this->sma.assign(n_elements, NAN);
    this->upper_band.assign(n_elements, NAN);
    this->lower_band.assign(n_elements, NAN);
    this->regions.assign(n_elements, 0);
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


void BollingerBands::detect_regions(size_t idx) {
    double price = (*this->prices)[idx];

    if (price < this->lower_band[idx]) // buy when price crosses below lower band
        this->regions[idx] = +1;
    else if (price > this->upper_band[idx])  // sell when price crosses above upper band
        this->regions[idx] = -1;
    else
        this->regions[idx] = 0;  // neutral region
}


