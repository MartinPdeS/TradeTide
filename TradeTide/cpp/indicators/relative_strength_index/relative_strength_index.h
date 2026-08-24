/**
 * @file relative_strength_index.h
 * @brief Relative Strength Index calculation and threshold-based trade regions.
 *
 * The implementation uses Wilder's smoothed average gains and losses. Regions
 * are encoded as ``+1`` below ``over_sold``, ``-1`` above ``over_bought``, and
 * ``0`` otherwise. The first ``window`` entries are undefined because there is
 * insufficient price history.
 */
#pragma once

#include "../base_indicator/base_indicator.h"

/**
 * @class RelativeStrengthIndex
 * @brief Momentum oscillator normalised to the closed interval [0, 100].
 *
 * @invariant window is positive and 0 <= over_sold < over_bought <= 100.
 * @note A flat price series has RSI 50 after the warm-up period.
 */
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

    /** @brief Calculate RSI values and threshold-derived regions for all prices. */
    void process() override;
    /** @brief Set the region for one already-computed RSI observation. */
    void detect_regions(size_t idx) override;
};
