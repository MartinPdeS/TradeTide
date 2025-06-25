#include "relative_momentum_index.h"

void RelativeMomentumIndex::process() {
    size_t n = prices->size();
    this->initialize(n);
    for (size_t i = 0; i < n; ++i) {
        this->update_momentum(i);
        this->update_smoothing(i);
        this->compute_rmi(i);
        this->detect_signal_from_region(i);
    }
}

void RelativeMomentumIndex::initialize(size_t n) {
    this->momentum.assign(n, NAN);
    this->rmi.assign(n, NAN);
    this->signals.assign(n, 0);
    this->sum_gain = sum_loss = 0.0;
}

void RelativeMomentumIndex::update_momentum(size_t idx) {
    if (idx >= momentum_period) {
        this->momentum[idx] = (*prices)[idx] - (*prices)[idx - momentum_period];
    }
}

void RelativeMomentumIndex::update_smoothing(size_t idx) {
    double m = momentum[idx];
    if (!std::isnan(m)) {
        if (m >= 0) sum_gain += m;
        else        sum_loss += -m;
    }
    // remove old
    size_t old_idx = idx >= smooth_period ? idx - smooth_period : std::string::npos;
    if (old_idx != std::string::npos && !std::isnan(momentum[old_idx])) {
        double old = this->momentum[old_idx];

        if (old >= 0)
            this->sum_gain -= old;
        else
            this->sum_loss -= -old;
    }
}

void RelativeMomentumIndex::compute_rmi(size_t idx) {
    if (idx >= momentum_period + smooth_period - 1) {
        double avg_gain = this->sum_gain / static_cast<double>(smooth_period);
        double avg_loss = this->sum_loss / static_cast<double>(smooth_period);
        double denom   = avg_gain + avg_loss;
        if (denom > 0) this->rmi[idx] = 100.0 * (avg_gain / denom);
        else           this->rmi[idx] = 50.0;
    }
}

void RelativeMomentumIndex::detect_regions(size_t idx) {
    if (std::isnan(this->rmi[idx])) {
        this->regions[idx] = 0;
        return;
    }

    double value = this->rmi[idx];

    if (value < this->over_sold)
        this->regions[idx] = +1;  // buy region (oversold)
    else if (value > this->over_bought)
        this->regions[idx] = -1; // sell region (overbought)
    else
        this->regions[idx] = 0;  // neutral region
}


