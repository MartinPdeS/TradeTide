#include "relative_strength_index.h"
#include <algorithm>

void RelativeStrengthIndex::process() {
    const size_t count = prices->size();
    rsi.assign(count, NAN);
    regions.assign(count, 0);
    if (count <= window) return;

    double gains = 0.0;
    double losses = 0.0;
    for (size_t index = 1; index <= window; ++index) {
        const double change = (*prices)[index] - (*prices)[index - 1];
        gains += std::max(change, 0.0);
        losses += std::max(-change, 0.0);
    }

    double average_gain = gains / static_cast<double>(window);
    double average_loss = losses / static_cast<double>(window);
    for (size_t index = window; index < count; ++index) {
        if (index > window) {
            const double change = (*prices)[index] - (*prices)[index - 1];
            average_gain = (average_gain * (window - 1) + std::max(change, 0.0)) / window;
            average_loss = (average_loss * (window - 1) + std::max(-change, 0.0)) / window;
        }
        if (average_gain == 0.0 && average_loss == 0.0) rsi[index] = 50.0;
        else if (average_loss == 0.0) rsi[index] = 100.0;
        else rsi[index] = 100.0 - 100.0 / (1.0 + average_gain / average_loss);
        detect_regions(index);
    }
}

void RelativeStrengthIndex::detect_regions(size_t idx) {
    if (rsi[idx] < over_sold) regions[idx] = 1;
    else if (rsi[idx] > over_bought) regions[idx] = -1;
}
