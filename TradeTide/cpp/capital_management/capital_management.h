#pragma once

#include "../position/position.h"
#include "../exit_strategy/exit_strategy.h"
#include "../state/state.h"

class BaseCapitalManagement {
public:
    double initial_capital;
    double max_capital_at_risk;
    size_t max_concurrent_positions;
    State *state;
    /// Positions selected from the pool that passed capital constraints.
    std::vector<PositionPtr> selected_positions;

    /// Positions currently active (open) during simulation.
    std::vector<PositionPtr> active_positions;

    /// All positions that were executed (closed or open).
    std::vector<PositionPtr> executed_positions;

    virtual ~BaseCapitalManagement() = default;
    BaseCapitalManagement(const double capital, const double max_capital_at_risk, const size_t max_concurrent_positions)
    : initial_capital(capital), max_capital_at_risk(max_capital_at_risk), max_concurrent_positions(max_concurrent_positions) {}
    /**
     * Computes the appropriate lot size for a given position.
     *
     * @param position The position for which to evaluate sizing.
     * @param equity   The current portfolio equity.
     * @return         The calculated lot size.
     */
    virtual void compute_lot_size(BasePosition& position) const = 0;

    virtual bool try_open_position(const PositionPtr& position) = 0;

    void reset_state() {
        this->selected_positions.clear();
        this->executed_positions.clear();
    }

    bool try_close_position(const PositionPtr& position) {
        this->state->equity += position->calculate_profit_and_loss();
        return true;
    }

};


class FixedFractional : public BaseCapitalManagement {
    public:
        explicit FixedFractional(const double capital, const double risk_per_trade, const double max_capital_at_risk, const size_t max_concurrent_positions)
            : BaseCapitalManagement(capital, max_capital_at_risk, max_concurrent_positions), risk_per_trade_(risk_per_trade) {}

        void compute_lot_size(BasePosition& position) const override {
            const double entry_price = position.entry_price;
            const double stop_price  = position.exit_strategy->stop_loss_price;
            const double pip_value   = position.market.pip_value;

            // Risk per pip in money
            const double price_diff = std::abs(entry_price - stop_price);

            if (this->state->equity <= 0.0) {
                position.lot_size = 0.0;
                return;
            }

            // Total amount of capital to risk on this trade
            const double capital_to_risk = this->state->equity * this->risk_per_trade_;

            // Compute lot size so that: lot_size * price_diff * pip_value == capital_to_risk
            double lot_size = capital_to_risk / (price_diff * pip_value);

            // Safety clamp
            if (std::isnan(lot_size) || std::isinf(lot_size) || lot_size <= 0.0) {
                position.lot_size = 0.0;
                return;
            }

            position.lot_size = lot_size;
        }

        bool try_open_position(const PositionPtr& position) override {
            // Compute lot size
            this->compute_lot_size(*position);

            if (this->state->number_of_concurrent_positions >= this->max_concurrent_positions)
                return false;

            // Skip if not enough capital to open
            if (position->lot_size == 0.0)
                return false;

            // Accept position
            this->active_positions.push_back(position);
            this->selected_positions.push_back(position);
            this->executed_positions.push_back(position);

            return true;
        }

    private:
        double risk_per_trade_;
};


class FixedLot : public BaseCapitalManagement {
    public:
        double fixed_lot;

        FixedLot(double capital, double fixed_lot, double max_capital_at_risk, size_t max_concurrent_positions)
            : BaseCapitalManagement(capital, max_capital_at_risk, max_concurrent_positions), fixed_lot(fixed_lot) {}

        void compute_lot_size(BasePosition& position) const override {
            position.lot_size = fixed_lot;
        }

        bool try_open_position(const PositionPtr& position) override {
            this->compute_lot_size(*position);
            if (this->state->number_of_concurrent_positions >= this->max_concurrent_positions)
                return false;
            if (position->lot_size == 0.0)
                return false;

            this->active_positions.push_back(position);
            this->selected_positions.push_back(position);
            this->executed_positions.push_back(position);

            return true;
        }
    };