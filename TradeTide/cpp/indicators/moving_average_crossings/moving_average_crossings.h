#pragma once

#include "../base_indicator/base_indicator.h"

class MovingAverageCrossing : public BaseIndicator {
public:
    size_t short_window;
    size_t long_window;
    std::vector<double> short_moving_average;
    std::vector<double> long_moving_average;

    /**
     * Constructor for the MovingAverageCrossing strategy.
     * Initializes the short and long moving average windows.
     * @param short_w The size of the short moving average window.
     * @param long_w The size of the long moving average window.
     */
    MovingAverageCrossing(size_t short_window, size_t long_window);
    MovingAverageCrossing() = default;


private:
    double sum_short = 0.0;
    double sum_long  = 0.0;

    /**
     * Process the moving average crossing strategy.
     * This method iterates through the price vector and computes the moving averages and signals.
     */
    void process();

    /**
     * Initialize the moving average vectors and sums.
     * This method should be called before processing any prices.
     * @param n The number of price points to initialize for.
     */
    void initialize(size_t n);

    /**
     * Update the running sums for short and long moving averages.
     * This method assumes that the index `idx` is valid and within bounds.
     * @param idx The current index in the price vector.
     * @param prices The vector of prices from which to compute the moving averages.
     */
    void update_sums(size_t idx);

    /**
     * Compute the moving averages for the current index.
     * This method assumes that the index `idx` is valid and within bounds.
     * @param idx The current index in the price vector.
     */
    void compute_mas(size_t idx);

    /**
     * Detect buy/sell signals based on price crossing the bands.
     * Generates +1 for buy, -1 for sell, or 0 for no signal.
     * @param idx Current index in the price vector.
     */
    void detect_regions(size_t idx);
};
