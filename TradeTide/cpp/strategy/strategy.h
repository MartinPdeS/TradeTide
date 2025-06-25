#pragma once

#include <vector>
#include <chrono>
#include "../indicators/base_indicator/base_indicator.h"
#include "../market/market.h"

using Duration = std::chrono::system_clock::duration;
using TimePoint = std::chrono::system_clock::time_point;


class Strategy {

    std::vector<std::shared_ptr<BaseIndicator>> indicators;

    Strategy() = default;

    void add_metrics(std::shared_ptr<BaseIndicator> indicator) {
        indicators.push_back(std::move(indicator));
    }


    std::vector<int> get_trade_signal(const Market& market) {
        BaseIndicator& last_indicator = *indicators.back();

        last_indicator.run_with_market(market);

        return last_indicator.signals;
    }
};
