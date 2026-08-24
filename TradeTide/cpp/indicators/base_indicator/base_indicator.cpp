#include "base_indicator.h"

void BaseIndicator::run_with_vector(const std::vector<double>& prices) {
    this->prices = &prices;
    this->market = nullptr;

    this->process();
}

void BaseIndicator::run_with_market(const Market& market) {
    this->prices = &market.ask.close;
    this->market = &market;

    this->process();
}
