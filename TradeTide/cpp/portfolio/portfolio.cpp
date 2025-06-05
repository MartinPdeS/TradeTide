#include "portfolio.h"



using Duration = std::chrono::system_clock::duration;
using TimePoint = std::chrono::system_clock::time_point;



double Portfolio::final_equity() const {
    return this->state.equity;
}

double Portfolio::peak_equity() const {
    return *std::max_element(this->record.equity.begin(), this->record.equity.end());
}

void Portfolio::close_position(PositionPtr& position, const size_t &position_idx) {
    this->active_positions.erase(this->active_positions.begin() + position_idx);
    this->state.number_of_concurrent_positions -= 1;
    this->state.capital += position->exit_price * position->lot_size;
    position->is_closed = true;
    double profit_loss = position->get_price_difference();

    if (profit_loss > 0)
        ++this->record.success_count;
    else if (profit_loss < 0)
        ++this->record.fail_count;
}

void Portfolio::open_position(PositionPtr& position, const BaseCapitalManagement &capital_management) {
    double lot_size = capital_management.compute_lot_size(*position);

    if (lot_size == 0.0)
        return; // Cannot open position with zero lot size

    position->lot_size = lot_size;

    this->active_positions.push_back(position);
    this->selected_positions.push_back(position);
    this->executed_positions.push_back(position);



    this->state.number_of_concurrent_positions += 1;
    this->state.capital -= position->entry_price * position->lot_size;
    position->is_closed = false;
}

void Portfolio::try_close_positions(BaseCapitalManagement& capital_management) {
    for (size_t i = 0; i < this->active_positions.size(); i++) {
        PositionPtr& position = this->active_positions[i];

        // Attempt to close position
        if (position->close_date == this->state.current_date && capital_management.can_close_position(position))
            this->close_position(position, i);

    }
}

void Portfolio::try_open_positions(BaseCapitalManagement& capital_management) {
    while (this->state.position_index < this->position_collection.positions.size()) {

        // If we reached the end of positions, stop trying to open new ones
        if (this->position_collection.positions[this->state.position_index]->start_date != this->state.current_date)
            break;

        PositionPtr& position = this->position_collection.positions[this->state.position_index];

        // If we can't open more positions now, skip this one (but advance index!)
        if (capital_management.can_open_position(position))
            this->open_position(position, capital_management);

        ++this->state.position_index;
    }

}

void Portfolio::simulate(BaseCapitalManagement& capital_management) {
    this->record.start_timer();

    this->selected_positions.clear();
    this->executed_positions.clear();
    this->active_positions.clear();

    this->state = State(this->position_collection.market, capital_management.initial_capital);
    this->record.initial_capital = capital_management.initial_capital;
    capital_management.state  = &this->state;

    for (PositionPtr& position : this->position_collection.positions)
        position->is_closed = false;

    for (size_t time_idx = 0; time_idx < this->position_collection.market.dates.size(); time_idx ++) {
        this->state.update_time_idx(time_idx);

        // Try to close opened positions
        this->try_close_positions(capital_management);

        // Try to activate new positions starting now
        this->try_open_positions(capital_management);

        if (time_idx == this->position_collection.market.dates.size() - 1)
            this->terminate_open_positions();

        state.capital_at_risk = this->calculate_capital_at_risk();
        state.equity = this->calculate_equity();
        this->record.update();
    }

    this->record.stop_timer();
}

void Portfolio::terminate_open_positions() {
    for (const auto& position : this->active_positions) {
        this->state.number_of_concurrent_positions -= 1;
        this->state.capital += position->exit_price * position->lot_size;
        position->is_closed = true;
    }

    this->active_positions.clear();
}

const std::vector<TimePoint>& Portfolio::get_market_dates() const {
    return this->position_collection.get_market().dates;
}

std::vector<BasePosition*> Portfolio::get_positions(size_t count) const {
    if (count == std::numeric_limits<size_t>::max())
        count = this->selected_positions.size();

    std::vector<BasePosition*> result;
    result.reserve(std::min(count, this->selected_positions.size()));

    for (const auto& up : this->selected_positions) {
        result.push_back(up.get());
        if (result.size() >= count)
            break;
    }

    return result;
}

double Portfolio::calculate_capital_at_risk() const {
    double total_risk = 0.0;

    for (const PositionPtr& position : this->active_positions)
        total_risk += std::abs(position->entry_price - position->exit_strategy->stop_loss_price) * position->lot_size;

    return total_risk;
}

double Portfolio::calculate_equity() const {
    double equity = this->state.capital;

    for (const PositionPtr& position : this->active_positions)
        equity += position->exit_price * position->lot_size;


    return equity;
}