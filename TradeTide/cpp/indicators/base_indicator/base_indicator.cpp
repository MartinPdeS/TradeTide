#pragma once

#include "../../market/market.h"

class BaseIndicator {
public:
    virtual ~BaseIndicator() = default;
    virtual void run_with_market(const Market& market) = 0;
    virtual void run_with_vector(const std::vector<double>& prices) = 0;
};