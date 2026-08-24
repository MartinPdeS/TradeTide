#pragma once

#include "../base_indicator/base_indicator.h"

class RelativeStrengthIndex : public BaseIndicator {
public:
    size_t window;
    double over_bought;
    double over_sold;
    std::vector<double> rsi;

    RelativeStrengthIndex(size_t window, double over_bought, double over_sold)
        : window(window), over_bought(over_bought), over_sold(over_sold) {
        assert(window > 0);
        assert(over_sold >= 0.0 && over_bought <= 100.0 && over_sold < over_bought);
    }

    void process() override;
    void detect_regions(size_t idx) override;
};
