#include "signal.h"




// Generate random signals
void Signal::generate_random(const double probability) {
    // 1) build a random raw state series with adjusted probabilities
    std::random_device rd;
    std::mt19937 gen(rd());

    // Define probability distributions for 0, 1, and -1
    double p_non_zero = probability;
    double p_zero = 1 - probability;

    std::uniform_real_distribution<> dist(0.0, 1.0);

    size_t n = this->market.dates.size();
    std::vector<int> raw;
    raw.reserve(n);

    // Generate signal values based on the adjusted probabilities
    for (size_t i = 0; i < n; ++i) {
        double random_value = dist(gen);

        if (random_value < p_zero) {
            raw.push_back(0);  // 90% chance to get 0
        } else if (random_value < p_zero + p_non_zero / 2) {
            raw.push_back(1);  // 5% chance to get +1
        } else {
            raw.push_back(-1); // 5% chance to get -1
        }
    }

    // 2) Compute the transition array
    trade_signal.clear();
    trade_signal.reserve(n);

    if (n == 0) return;

    // At index 0, we assume “no prior state” → no transition
    trade_signal.push_back(0);

    for (size_t i = 1; i < n; ++i) {
        if (raw[i] == 1 && raw[i-1] != 1)
            trade_signal.push_back(1);
        else if (raw[i] == -1 && raw[i-1] != -1)
            trade_signal.push_back(-1);
        else
            trade_signal.push_back(0);
    }
}



// Get signal array
const std::vector<int>&
Signal::get_signals() const {
    return trade_signal;
}

// Display signals
void
Signal::display_signal() const {
    std::cout << "Signals:\n";

    for (size_t i = 0; i < trade_signal.size(); ++i)
        std::cout << "Interval " << i + 1 << ": " << trade_signal[i] << "\n";

}
