#include "portfolio.h"
#include <iostream>
#include <iomanip>

double Portfolio::final_equity() const {
    return this->capital_management.current_equity;
}

double Portfolio::peak_equity() const {
    if (this->equity_history.empty())
        return this->capital_management.initial_capital;

    return *std::max_element(this->equity_history.begin(), this->equity_history.end());
}

std::vector<double> Portfolio::equity_curve() const {
    return this->equity_history;
}

void Portfolio::simulate() {
    this->reset_state();

    const auto& dates = this->position_collection.get_market().dates;
    const auto& all_positions = this->position_collection.positions;

    size_t position_index = 0;

    for (size_t time_idx = 0; time_idx < dates.size(); ++time_idx) {
        const TimePoint& current_time = dates[time_idx];

        this->finalize_closed_positions();
        this->activate_positions_at(current_time, all_positions, position_index);
    }

    this->finalize_remaining_open_positions();

    this->compute_open_position_count_over_time();
    this->compute_equity_over_time();
}


void Portfolio::reset_state() {
    this->capital_management.current_equity = this->capital_management.initial_capital;
    this->active_positions.clear();
    this->selected_positions.clear();
}

void Portfolio::finalize_closed_positions() {
    for (auto it = this->active_positions.begin(); it != this->active_positions.end();) {
        PositionPtr& position = *it;

        this->capital_management.compute_lot_size(*position);

        if (position->is_closed) {
            this->capital_management.current_equity += position->calculate_profit_and_loss();
            it = this->active_positions.erase(it);
        } else
            ++it;
    }
}

void Portfolio::activate_positions_at(const TimePoint& current_time, const std::vector<PositionPtr>& all_positions, size_t& position_index) {
    while (position_index < all_positions.size() && all_positions[position_index]->start_date == current_time) {

        std::cout<<this->active_positions.size()<<"   :: "<<this->capital_management.max_concurrent_positions<<"\n";
        if (this->active_positions.size() >= this->capital_management.max_concurrent_positions)
            break;

        const PositionPtr& position = all_positions[position_index];
        this->capital_management.compute_lot_size(*position);

        this->active_positions.push_back(position);
        this->selected_positions.push_back(position);

        ++position_index;
    }
}

void Portfolio::finalize_remaining_open_positions() {
    for (PositionPtr& position : this->active_positions) {
        this->capital_management.compute_lot_size(*position);

        if (!position->is_closed)
            position->close(position->open_idx);

        this->capital_management.current_equity += position->calculate_profit_and_loss();
    }

    this->active_positions.clear();
}



void Portfolio::display() const {
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Portfolio Summary:\n";
    std::cout << "------------------\n";
    std::cout << "Final Equity:         " << this->final_equity() << "\n";
    std::cout << "Peak Equity:          " << this->peak_equity() << "\n";
    std::cout << "Positions Executed:   " << this->executed_positions.size() << "\n";
    ;
}


void Portfolio::compute_open_position_count_over_time() {
    const std::vector<TimePoint>& dates = this->position_collection.get_market().dates;

    this->open_position_count.clear();
    this->open_position_count.reserve(dates.size());

    size_t count;
    for (size_t i = 0; i < dates.size(); ++i) {
        count = 0;
        for (const PositionPtr& position : this->selected_positions)
            if (position->is_open(dates[i]))
                count++;

        this->open_position_count.push_back(count);
    }
}

void Portfolio::compute_equity_over_time() {
    const std::vector<TimePoint>& dates = this->position_collection.get_market().dates;

    this->equity_history.clear();
    this->equity_history.reserve(dates.size());

    for (size_t i = 0; i < dates.size(); ++i) {
        const TimePoint& current_time = dates[i];
        double equity = this->capital_management.initial_capital;

        for (const PositionPtr& position : this->selected_positions) {
            if (position->is_closed && position->close_date <= current_time) {
                equity += position->calculate_profit_and_loss();
            }
        }

        this->equity_history.push_back(equity);
    }
}

const std::vector<TimePoint>& Portfolio::get_market_dates() const {
    return this->position_collection.get_market().dates;
}
