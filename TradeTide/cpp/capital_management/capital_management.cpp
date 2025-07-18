#include "capital_management.h"

#include "../position/position.h"



// ---------- BaseCapitalManagement Implementation -----------------------------
double BaseCapitalManagement::can_open_position(const PositionPtr& position) {
    if (this->state->capital <= 0.0) // Cannot open position if capital is zero or negative
        return 0.0;

    // Limit maximum concurrent positions
    if (this->state->number_of_concurrent_positions >= this->max_concurrent_positions)
        return 0.0;

    // Enforce max capital-at-risk threshold
    const double projected_risk = this->state->capital_at_risk + position->get_capital_at_risk();
    if (projected_risk > this->max_capital_at_risk)
        return 0.0;

    return this->compute_lot_size(*position);
}

// ---------- FixedLot Implementation -----------------------------
double FixedLot::compute_lot_size(BasePosition& position) const {
    double value  = position.entry_price * this->fixed_lot_size;

    if (value > this->state->capital)  // If the value exceeds available capital, return 0.0 to indicate no position can be opened
        return 0.0;

    return this->fixed_lot_size;
}


// ---------- FixedFractional Implementation -----------------------------
double FixedFractional::compute_lot_size(BasePosition& position) const {
    const double entry_price = position.entry_price;
    const double stop_price  = position.exit_strategy->stop_loss_price;

    // Risk in monetary units (e.g., USD)
    const double price_risk = std::abs(entry_price - stop_price);

    // Capital allocated to this trade (e.g., 1% of equity)
    const double capital_to_risk = this->state->capital * this->risk_fraction;

    // Lot size needed to expose 'capital_to_risk' to the defined price movement
    double lot_size = capital_to_risk / price_risk;

    // Final validation: must be positive and finite
    return (std::isfinite(lot_size) && lot_size > 0.0) ? lot_size : 0.0;
}
