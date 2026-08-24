/**
 * @file macd.h
 * @brief Moving Average Convergence Divergence indicator implementation.
 *
 * MACD is the difference of fast and slow exponential moving averages. Its
 * signal line is an EMA of that difference. A region is emitted only when the
 * histogram crosses zero, avoiding a repeated direction signal on every bar.
 */
#pragma once

#include "../base_indicator/base_indicator.h"

/**
 * @class MACD
 * @brief EMA-based trend and momentum indicator with crossover regions.
 *
 * @invariant fast_window < slow_window and all windows are positive.
 * @note Values before the slow and signal warm-up periods are NaN.
 */
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

    /** @brief Calculate the MACD, signal, histogram, and crossover regions. */
    void process() override;
    /** @brief Emit +1/-1 when the histogram crosses above/below zero. */
    void detect_regions(size_t idx) override;
};
