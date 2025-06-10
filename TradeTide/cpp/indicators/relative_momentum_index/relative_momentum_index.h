#pragma once

#include "../base_indicator/base_indicator.h"

/**
 * Relative Momentum Index (RMI) indicator.
 * Computes momentum over a given period and applies an RSI-like calculation
 * with a smoothing period. Optionally generates over_bought/over_sold signals.
 */
class RelativeMomentumIndex : public BaseIndicator {
public:
    size_t momentum_period;
    size_t smooth_period;
    double over_bought;
    double over_sold;

    std::vector<double> momentum;
    std::vector<double> rmi;

    /**
     * Construct an RMI indicator.
     * @param momentum_period Number of periods for momentum calculation.
     * @param smooth_period Number of periods for smoothing averages.
     * @param over_bought Threshold above which to signal sell.
     * @param over_sold Threshold below which to signal buy.
     */
    RelativeMomentumIndex(size_t momentum_period, size_t smooth_period, double over_bought, double over_sold)
        : momentum_period(momentum_period),
          smooth_period(smooth_period),
          over_bought(over_bought),
          over_sold(over_sold)
    {
        assert(momentum_period > 0 && smooth_period > 0);
    }

    RelativeMomentumIndex() = default;

private:
    double sum_gain = 0.0;
    double sum_loss = 0.0;

    void process();

    void initialize(size_t n);

    void update_momentum(size_t idx);

    void update_smoothing(size_t idx);

    void compute_rmi(size_t idx);

    void detect_signal(size_t idx);
};
