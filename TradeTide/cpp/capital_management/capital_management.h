#pragma once

#include <vector>

#include "../position/position.h"
#include "../exit_strategy/exit_strategy.h"
#include "../state/state.h"

/**
 * @brief Abstract base class for capital management policies.
 *
 * Manages capital constraints such as max concurrent positions and max capital at risk.
 */
class BaseCapitalManagement {
public:
    double initial_capital;
    double max_capital_at_risk;
    size_t max_concurrent_positions;
    State* state = nullptr;

    std::vector<PositionPtr> selected_positions;  ///< Positions accepted for simulation
    std::vector<PositionPtr> active_positions;    ///< Currently open positions
    std::vector<PositionPtr> executed_positions;  ///< All positions ever opened

    virtual ~BaseCapitalManagement() = default;

    BaseCapitalManagement(double capital, double max_risk, size_t max_positions)
        : initial_capital(capital),
          max_capital_at_risk(max_risk),
          max_concurrent_positions(max_positions) {}

    /**
     * @brief Compute and assign the lot size for a position using fixed fractional logic.
     *
     * The lot size is calculated to risk `risk_fraction` of current equity, given the monetary distance
     * between entry price and stop-loss price. No safety assertions are enforced here—if invalid inputs
     * are given (e.g., zero stop distance), resulting lot size may be infinite or zero.
     */
    virtual void compute_lot_size(BasePosition& position) const = 0;

    /**
     * @brief Attempt to open a position based on risk constraints.
     * @return true if accepted, false if rejected.
     */
    virtual bool try_open_position(const PositionPtr& position) = 0;

    /**
     * @brief Remove position from active pool and update equity.
     */
    bool try_close_position(const PositionPtr&) {
        return true;
    }

    void reset_state() {
        this->selected_positions.clear();
        this->executed_positions.clear();
        this->active_positions.clear();
    }
};

/**
 * @brief Fixed Lot Capital Management.
 *
 * Opens positions with a constant, predefined lot size regardless of equity or price movement.
 */
class FixedLot : public BaseCapitalManagement {
    private:
        double fixed_lot_size;  ///< Constant lot size for all trades

    public:
        FixedLot(double capital, double fixed_lot_size, double max_capital_at_risk, size_t max_concurrent_positions)
            : BaseCapitalManagement(capital, max_capital_at_risk, max_concurrent_positions),
              fixed_lot_size(fixed_lot_size) {}

        void compute_lot_size(BasePosition& position) const override;

        bool try_open_position(const PositionPtr& position) override;
    };

/**
 * @brief Fixed Fractional Capital Management.
 *
 * This strategy risks a fixed fraction of current equity on each trade,
 * with the lot size determined by the stop-loss distance (price risk).
 */
class FixedFractional : public BaseCapitalManagement {
    private:
        double risk_fraction;  ///< Fraction of equity to risk per trade (e.g., 0.01 = 1%)

    public:
        FixedFractional(double capital, double risk_fraction, double max_capital_at_risk, size_t max_concurrent_positions)
            : BaseCapitalManagement(capital, max_capital_at_risk, max_concurrent_positions),
              risk_fraction(risk_fraction) {}


        void compute_lot_size(BasePosition& position) const override;

        bool try_open_position(const PositionPtr& position) override;
    };

