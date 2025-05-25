#include "capital_management.h"

#include "../position/position.h"

void FixedLot::compute_lot_size(BasePosition& position) const {
    position.lot_size = this->fixed_lot_size;
}

bool FixedLot::try_open_position(const PositionPtr& position) {
    this->compute_lot_size(*position);

    if (this->state->number_of_concurrent_positions >= this->max_concurrent_positions)
        return false;

    if (position->lot_size == 0.0)
        return false;

    const double projected_risk = this->state->capital_at_risk + position->get_capital_at_risk();
    if (projected_risk > this->max_capital_at_risk)
        return false;

    this->active_positions.push_back(position);
    this->selected_positions.push_back(position);
    this->executed_positions.push_back(position);

    return true;
}


void FixedFractional::compute_lot_size(BasePosition& position) const {
    const double entry_price = position.entry_price;
    const double stop_price  = position.exit_strategy->stop_loss_price;

    // Risk in monetary units (e.g., USD)
    const double price_risk = std::abs(entry_price - stop_price);

    // Capital allocated to this trade (e.g., 1% of equity)
    const double capital_to_risk = this->state->capital * this->risk_fraction;

    // Lot size needed to expose 'capital_to_risk' to the defined price movement
    double lot_size = capital_to_risk / price_risk;

    // Final validation: must be positive and finite
    position.lot_size = (std::isfinite(lot_size) && lot_size > 0.0) ? lot_size : 0.0;
}


bool FixedFractional::try_open_position(const PositionPtr& position) {
    this->compute_lot_size(*position);

    // Limit maximum concurrent positions
    if (this->state->number_of_concurrent_positions >= this->max_concurrent_positions)
        return false;

    // Reject if lot size is invalid
    if (position->lot_size == 0.0)
        return false;

    // Enforce max capital-at-risk threshold
    const double projected_risk = this->state->capital_at_risk + position->get_capital_at_risk();
    if (projected_risk > this->max_capital_at_risk)
        return false;

    // Accept the position
    this->active_positions.push_back(position);
    this->selected_positions.push_back(position);
    this->executed_positions.push_back(position);

    return true;
}


