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

    for (const TimePoint& current_time : dates) {
        this->current_time = current_time;

        // Finalize positions whose close_date <= current_time
        for (auto it = this->active_positions.begin(); it != this->active_positions.end();) {
            const PositionPtr& pos = *it;

            if (pos->close_date <= current_time) {
                this->capital_management.current_equity += pos->calculate_profit_and_loss();
                it = this->active_positions.erase(it);
            }
            else
                ++it;
        }

        // ➕ Try to activate new positions starting now
        while (position_index < all_positions.size() && all_positions[position_index]->start_date == current_time) {

        const PositionPtr& pos = all_positions[position_index];

        // If we can't open more positions now, skip this one (but advance index!)
        if (this->active_positions.size() >= this->capital_management.max_concurrent_positions) {
            ++position_index;
            continue;
        }

        // Compute lot size
        this->capital_management.compute_lot_size(*pos);

        // Skip if not enough capital to open
        if (pos->lot_size == 0.0) {
            ++position_index;
            continue;
        }

        // Accept position
        this->active_positions.push_back(pos);
        this->selected_positions.push_back(pos);
        this->executed_positions.push_back(pos);

        ++position_index;
    }


        // Track portfolio state at this time
        this->open_position_count.push_back(this->active_positions.size());
        this->equity_history.push_back(this->capital_management.current_equity);
    }

    // 📌 Close all remaining positions at end
    for (const auto& pos : this->active_positions) {
        this->capital_management.current_equity += pos->calculate_profit_and_loss();
    }

    std::cout<<"this->selected_positions.size() = "<<this->selected_positions.size()<<std::endl;
    this->active_positions.clear();
}


void Portfolio::reset_state() {
    this->capital_management.current_equity = this->capital_management.initial_capital;
    this->selected_positions.clear();
    this->executed_positions.clear();
    this->equity_history.clear();
    this->open_position_count.clear();
}



void Portfolio::display() const {
    for (const PositionPtr& e : this->selected_positions)
        e->display();

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
        this->current_time = dates[i];
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

std::vector<BasePosition*> Portfolio::get_positions(size_t count) const {
    if (count == std::numeric_limits<size_t>::max()) {
        count = this->selected_positions.size();
    }

    std::vector<BasePosition*> result;
    result.reserve(std::min(count, this->selected_positions.size()));

    for (const auto& up : this->selected_positions) {
        result.push_back(up.get());
        if (result.size() >= count) break;
    }

    return result;
}