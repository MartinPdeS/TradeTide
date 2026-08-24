#pragma once

#include "../base_indicator/base_indicator.h"

class MACD : public BaseIndicator {
public:
    size_t fast_window;
    size_t slow_window;
    size_t signal_window;
    std::vector<double> macd;
    std::vector<double> signal;
    std::vector<double> histogram;

    MACD(size_t fast_window, size_t slow_window, size_t signal_window)
        : fast_window(fast_window), slow_window(slow_window), signal_window(signal_window) {
        assert(fast_window > 0 && fast_window < slow_window && signal_window > 0);
    }

    void process() override;
    void detect_regions(size_t idx) override;
};
