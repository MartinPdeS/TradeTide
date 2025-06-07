#include "../base_indicator/base_indicator.h"

/**
 * BollingerBands indicator computes a simple moving average (SMA) and
 * upper/lower bands based on a standard deviation multiplier.
 * Optionally generates buy/sell signals when price crosses bands.
 */
class BollingerBands : public BaseIndicator {
public:
    std::vector<double> sma;
    std::vector<double> upper_band;
    std::vector<double> lower_band;
    size_t window;
    double multiplier;

    /**
     * Construct BollingerBands with given window and multiplier.
     * @param window Size of the moving window for SMA and stddev.
     * @param multiplier Number of standard deviations for the bands.
     */
    BollingerBands(size_t window, double multiplier) : window(window), multiplier(multiplier)
    {
        assert(window > 0 && "window size must be positive");
        assert(multiplier > 0.0 && "multiplier must be positive");
    }

    BollingerBands() = default;

private:
    double sum = 0.0;
    double sum_sq = 0.0;

    /**
     * Process the Bollinger Bands indicator.
     * This method computes the SMA, upper/lower bands, and signals.
     */
    void process();

    /**
     * Initialize vectors and sums for processing.
     * @param n Number of price points to initialize for.
     */
    void initialize(size_t n);

    /**
     * Update the rolling sum and sum of squares for the current window.
     * @param idx Current index in the price vector.
     */
    void update_window(size_t idx);

    /**
     * Update the rolling sum and sum of squares for the current window.
     * @param idx Current index in the price vector.
     */
    void compute_bands(size_t idx);

    /**
     * Detect buy/sell signals based on price crossing the bands.
     * Generates +1 for buy, -1 for sell, or 0 for no signal.
     * @param idx Current index in the price vector.
     */
    void detect_signal(size_t idx);
};
