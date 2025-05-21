#pragma once

#include "../position/position.h"
#include "../exit_strategy/exit_strategy.h"

class BaseCapitalManagement {
public:
    double initial_capital;
    double capital;

    size_t max_lot_size;
    double max_capital_at_risk;
    size_t max_concurrent_positions;

    double current_equity;
    size_t position_count;

    virtual ~BaseCapitalManagement() = default;
    BaseCapitalManagement(const double capital, const size_t max_lot_size, const double max_capital_at_risk, const size_t max_concurrent_positions)
    : initial_capital(capital), capital(capital), max_lot_size(max_lot_size), max_capital_at_risk(max_capital_at_risk), max_concurrent_positions(max_concurrent_positions) {}
    /**
     * Computes the appropriate lot size for a given position.
     *
     * @param position The position for which to evaluate sizing.
     * @param equity   The current portfolio equity.
     * @return         The calculated lot size.
     */
    virtual void compute_lot_size(BasePosition& position) const = 0;
};


class FixedFractionalCapitalManagement : public BaseCapitalManagement {
    public:
        explicit FixedFractionalCapitalManagement(const double capital, const double risk_per_trade, const size_t max_lot_size, const double max_capital_at_risk, const size_t max_concurrent_positions)
            : BaseCapitalManagement(capital, max_lot_size, max_capital_at_risk, max_concurrent_positions), risk_per_trade_(risk_per_trade) {}

        void compute_lot_size(BasePosition& position) const override {
            const double entry_price = position.entry_price;
            const double stop_price = position.exit_strategy->stop_loss_price;
            const double pip_value = position.market.pip_value;

            double pip_risk = std::abs(entry_price - stop_price) / pip_value;
            if (pip_risk <= 0.0 || pip_value <= 0.0)
                return;  // fallback

            double capital_risk = this->current_equity * this->risk_per_trade_;
            double lot_size = capital_risk / (pip_risk * pip_value);

            position.lot_size = lot_size;
        }

    private:
        double risk_per_trade_;
    };
