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

    virtual ~BaseCapitalManagement() = default;

    BaseCapitalManagement(double capital, double max_risk, size_t max_positions)
        : initial_capital(capital), max_capital_at_risk(max_risk), max_concurrent_positions(max_positions) {}

    /**
     * @brief Compute and assign the lot size for a position using fixed fractional logic.
     *
     * The lot size is calculated to risk `risk_fraction` of current equity, given the monetary distance
     * between entry price and stop-loss price. No safety assertions are enforced here—if invalid inputs
     * are given (e.g., zero stop distance), resulting lot size may be infinite or zero.
     */
    virtual double compute_lot_size(BasePosition& position) const = 0;

    /**
     * @brief Attempts to open a position based on the fixed lot strategy.
     *
     * This method checks if the position can be opened under the current capital constraints.
     * @param position The position to open.
     * @return true if the position is accepted, false otherwise.
     */
    double can_open_position(const PositionPtr& position);

    /**
     * @brief Remove position from active pool and update equity.
     */
    bool can_close_position(const PositionPtr&) {
        return true;
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
            : BaseCapitalManagement(capital, max_capital_at_risk, max_concurrent_positions), fixed_lot_size(fixed_lot_size) {}

        /**
         * @brief Computes the lot size for a position based on the fixed lot strategy.
         *
         * This method assigns the fixed lot size to the position.
         */
        double compute_lot_size(BasePosition& position) const override;


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
            : BaseCapitalManagement(capital, max_capital_at_risk, max_concurrent_positions), risk_fraction(risk_fraction) {}

        /**
         * @brief Computes the lot size for a position based on the fixed fractional strategy.
         *
         * This method calculates the lot size to risk a fixed fraction of equity
         * based on the stop-loss distance.
         */
        double compute_lot_size(BasePosition& position) const override;
    };
