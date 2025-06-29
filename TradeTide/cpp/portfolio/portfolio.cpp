#include "portfolio.h"



using Duration = std::chrono::system_clock::duration;
using TimePoint = std::chrono::system_clock::time_point;




// ---------------- Constructor ----------------
Portfolio::Portfolio(PositionCollection& position_collection, bool debug_mode): position_collection(position_collection), debug_mode(debug_mode) {
    this->record.state = &this->state;
    this->record.start_record(this->position_collection.market.dates.size());

    if (this->debug_mode) {
        printf("[DEBUG: PORTFOLIO - CONSTRUCT] Portfolio constructed with %zu market dates\n", this->position_collection.market.dates.size());
    }
}



// ---------------- Public Methods ----------------
Metrics Portfolio::get_metrics() {
    Metrics metrics(this->record);
    metrics.calculate();
    return metrics;
}

void Portfolio::display() const {
    for (const auto& position : this->executed_positions) {
        position->display();
    }
}


// ---------------- Equity and Performance ----------------
double Portfolio::final_equity() const {
    return this->state.equity;
}

double Portfolio::peak_equity() const {
    return *std::max_element(this->record.equity.begin(), this->record.equity.end());
}


// ---------------- Position Management ----------------
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

    if (this->debug_mode) {
        printf("[DEBUG: PORTFOLIO - CLOSE] Closed position at price %.2f, PnL: %.2f\n",
               position->exit_price, profit_loss);
    }
}


void Portfolio::open_position(PositionPtr& position) {
    double lot_size = this->capital_management->compute_lot_size(*position);

    if (lot_size == 0.0) {
        if (this->debug_mode)
            printf("[DEBUG: PORTFOLIO - OPEN] Skipping position: computed lot size is 0.0\n");
        return;
    }

    position->lot_size = lot_size;
    this->active_positions.push_back(position);
    this->selected_positions.push_back(position);
    this->executed_positions.push_back(position);

    this->state.number_of_concurrent_positions += 1;
    this->state.capital -= position->entry_price * position->lot_size;
    position->is_closed = false;

    if (this->debug_mode) {
        printf("[DEBUG: PORTFOLIO - OPEN] Opened position at price %.2f, lot size %.2f\n",
               position->entry_price, position->lot_size);
    }
}

void Portfolio::try_close_positions() {
    for (size_t i = 0; i < this->active_positions.size(); i++) {
        PositionPtr& position = this->active_positions[i];

        // Attempt to close position
        if (position->close_date == this->state.current_date && this->capital_management->can_close_position(position))
            this->close_position(position, i);

    }
}

void Portfolio::try_open_positions() {
    while (this->state.position_index < this->position_collection.positions.size()) {

        // If we reached the end of positions, stop trying to open new ones
        if (this->position_collection.positions[this->state.position_index]->start_date != this->state.current_date)
            break;

        PositionPtr& position = this->position_collection.positions[this->state.position_index];

        // If we can't open more positions now, skip this one (but advance index!)
        if (this->capital_management->can_open_position(position))
            this->open_position(position);

        ++this->state.position_index;
    }

}

void Portfolio::simulate(BaseCapitalManagement& capital_management) {
    this->selected_positions.clear();
    this->executed_positions.clear();
    this->active_positions.clear();

    this->capital_management = &capital_management;

    this->state = State(this->position_collection.market, this->capital_management->initial_capital);
    this->record.initial_capital = this->capital_management->initial_capital;
    this->capital_management->state  = &this->state;

    this->position_collection.set_all_position_to_open();

    for (size_t time_idx = 0; time_idx < this->position_collection.market.dates.size(); time_idx++) {
        this->state.update_time_idx(time_idx);

        if (this->debug_mode) {
            printf("[DEBUG: PORTFOLIO - SIMULATE] Time step %zu / %zu\n", time_idx, this->position_collection.market.dates.size());
        }

        this->try_close_positions();
        this->try_open_positions();

        if (time_idx == this->position_collection.market.dates.size() - 1)
            this->terminate_open_positions();

        this->state.capital_at_risk = this->calculate_capital_at_risk();
        this->state.equity = this->calculate_equity();
        this->record.update();

        if (this->debug_mode) {
            printf("[DEBUG: PORTFOLIO - SIMULATE] Capital: %.2f, Equity: %.2f, At Risk: %.2f\n",
                this->state.capital, this->state.equity, this->state.capital_at_risk);
        }
    }
}

void Portfolio::terminate_open_positions() {
    for (const auto& position : this->active_positions) {
        this->state.number_of_concurrent_positions -= 1;
        this->state.capital += position->exit_price * position->lot_size;
        position->is_closed = true;
        this->executed_positions.push_back(position);

        if (this->debug_mode) {
            printf("[DEBUG: PORTFOLIO - TERMINATE] Terminating position at exit price %.2f with lot size %.2f\n",
                   position->exit_price, position->lot_size);
        }
    }

    if (this->debug_mode) {
        printf("[DEBUG: PORTFOLIO - TERMINATE] All remaining open positions have been terminated. Total: %zu\n",
               this->active_positions.size());
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