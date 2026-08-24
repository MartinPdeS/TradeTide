#include "macd.h"

void MACD::process() {
    const size_t count = prices->size();
    macd.assign(count, NAN);
    signal.assign(count, NAN);
    histogram.assign(count, NAN);
    regions.assign(count, 0);
    if (count == 0) return;

    const double fast_alpha = 2.0 / (fast_window + 1.0);
    const double slow_alpha = 2.0 / (slow_window + 1.0);
    const double signal_alpha = 2.0 / (signal_window + 1.0);
    double fast_ema = (*prices)[0];
    double slow_ema = (*prices)[0];
    double signal_ema = 0.0;

    for (size_t index = 0; index < count; ++index) {
        if (index > 0) {
            fast_ema += fast_alpha * ((*prices)[index] - fast_ema);
            slow_ema += slow_alpha * ((*prices)[index] - slow_ema);
        }
        if (index + 1 < slow_window) continue;
        macd[index] = fast_ema - slow_ema;
        if (index + 1 == slow_window) signal_ema = macd[index];
        else signal_ema += signal_alpha * (macd[index] - signal_ema);
        if (index + 1 < slow_window + signal_window - 1) continue;
        signal[index] = signal_ema;
        histogram[index] = macd[index] - signal[index];
        detect_regions(index);
    }
}

void MACD::detect_regions(size_t idx) {
    if (idx == 0 || std::isnan(histogram[idx]) || std::isnan(histogram[idx - 1])) return;
    if (histogram[idx - 1] <= 0.0 && histogram[idx] > 0.0) regions[idx] = 1;
    else if (histogram[idx - 1] >= 0.0 && histogram[idx] < 0.0) regions[idx] = -1;
}
