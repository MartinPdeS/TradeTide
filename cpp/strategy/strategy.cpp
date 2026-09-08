#include "strategy.h"


void Strategy::add_indicator(std::shared_ptr<BaseIndicator> indicator) {
    indicators.push_back(std::move(indicator));
}

std::vector<int> Strategy::get_trade_signal(const Market& market) {
    std::vector<std::vector<int>> signals;

    for (std::shared_ptr<BaseIndicator>& indicator : this->indicators){
        indicator->run_with_market(market);
        signals.push_back(this->get_signal_from_indicator(*indicator));
    }

    return this->combine_signals(signals);
}

std::vector<int> Strategy::get_signal_from_indicator(const BaseIndicator& indicator) {
    std::vector<int> signal;

    const size_t n_elements = indicator.regions.size();

    signal.assign(n_elements, 0);

    signal[0] = 0;
    for (size_t idx = 1; idx < n_elements; ++idx) {

        int region_now  = indicator.regions[idx];
        int region_prev = indicator.regions[idx - 1];

        if (region_now != 0 && region_prev == 0)  // crossing into buy or sell region
            signal[idx] = region_now;
        else  // no signal on continuation
            signal[idx] = 0;
    }

    return signal;
}

std::vector<int> Strategy::combine_signals(const std::vector<std::vector<int>>& signals, double threshold) {
    size_t num_indicators = signals.size();
    if (num_indicators == 0) return {};

    std::vector<double> weights(num_indicators, 1.0);  // all weights = 1.0
    return combine_signals(signals, weights, threshold);
}

std::vector<int> Strategy::combine_signals(const std::vector<std::vector<int>>& signals, const std::vector<double>& weights, double threshold) {
    size_t num_indicators = signals.size();
    if (num_indicators == 0) return {};

    size_t num_timesteps = signals[0].size();
    std::vector<int> final_signals(num_timesteps, 0);

    for (size_t t = 0; t < num_timesteps; ++t) {
        double score = 0.0;
        for (size_t i = 0; i < num_indicators; ++i) {
            score += weights[i] * signals[i][t];
        }

        if (score > threshold)
            final_signals[t] = +1;
        else if (score < -threshold)
            final_signals[t] = -1;
        else
            final_signals[t] = 0;
    }

    return final_signals;
}
