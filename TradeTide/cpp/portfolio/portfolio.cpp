#include "portfolio.h"
#include <iostream>
#include <iomanip>

double Portfolio::final_equity() const {
    return this->equity;
}

double Portfolio::peak_equity() const {
    if (this->equity_history.empty())
        return this->initial_capital;

    return *std::max_element(this->equity_history.begin(), this->equity_history.end());
}

std::vector<double> Portfolio::equity_curve() const {
    return this->equity_history;
}

void Portfolio::simulate() {
    this->equity = this->initial_capital;
    this->active_positions.clear();
    this->executed_positions.clear();
    this->equity_history.clear();

    const std::vector<TimePoint>& dates = this->position_collection.get_market().dates;
    const std::vector<PositionPtr>& all_positions = this->position_collection.positions;
    this->equity_history.reserve(dates.size());

    size_t position_index = 0;

    for (size_t time_idx = 0; time_idx < dates.size(); ++time_idx) {
        const TimePoint& current_time = dates[time_idx];

        // Finalize closed positions
        for (auto it = this->active_positions.begin(); it != this->active_positions.end();) {
            PositionPtr& position = *it;

            // Ensure lot size is set before computing PnL
            if (position->lot_size == 0.0)
                position->lot_size = std::min(1.0, this->max_lot_size);

            if (position->is_closed) {
                this->equity += position->calculate_profit_and_loss();
                position->display();
                it = this->active_positions.erase(it);
            } else {
                ++it;
            }
        }

        // Launch new positions starting at current time
        while (position_index < all_positions.size() &&
               all_positions[position_index]->start_date == current_time) {

            if (this->active_positions.size() >= this->max_concurrent_positions)
                break;

            const PositionPtr& position = all_positions[position_index];

            // Assign lot size *before anything else*
            position->lot_size = std::min(1.0, this->max_lot_size);

            this->active_positions.push_back(position);
            this->executed_positions.push_back(position);

            ++position_index;
        }

        this->equity_history.push_back(this->equity);
    }

    // Finalize any still-open positions
    for (const PositionPtr& position : this->active_positions) {
        if (position->lot_size == 0.0)
            position->lot_size = std::min(1.0, this->max_lot_size);

        if (!position->is_closed)
            position->close(position->start_idx);

        this->equity += position->calculate_profit_and_loss();
        this->equity_history.push_back(this->equity);
    }

    this->active_positions.clear();
}




void Portfolio::display() const {
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Portfolio Summary:\n";
    std::cout << "------------------\n";
    std::cout << "Initial Capital:      " << this->initial_capital << "\n";
    std::cout << "Final Equity:         " << this->final_equity() << "\n";
    std::cout << "Peak Equity:          " << this->peak_equity() << "\n";
    std::cout << "Positions Executed:   " << this->executed_positions.size() << "\n";
    std::cout << "Max Concurrent Pos.:  " << this->max_concurrent_positions << "\n";
    std::cout << "Max Lot Size:         " << this->max_lot_size << "\n";
    std::cout << "Max Capital at Risk:  " << this->max_capital_at_risk * 100 << " %\n\n";
}


std::vector<size_t> Portfolio::open_position_count_over_time() const {
    const std::vector<TimePoint>& dates = this->position_collection.get_market().dates;
    std::vector<size_t> open_count(dates.size(), 0);

    for (const PositionPtr& position : this->executed_positions) {
        for (size_t i = 0; i < dates.size(); ++i) {
            if (dates[i] >= position->start_date && dates[i] < position->close_date) {
                ++open_count[i];
            }
        }
    }

    return open_count;
}

const std::vector<TimePoint>& Portfolio::get_market_dates() const {
    return this->position_collection.get_market().dates;
}

std::vector<double> Portfolio::equity_over_time() const {
    const std::vector<TimePoint>& dates = this->position_collection.get_market().dates;
    std::vector<double> equity_series(dates.size(), this->initial_capital);

    double equity = this->initial_capital;

    // Collect all close events
    struct CloseEvent {
        size_t time_idx;
        double profit;
    };

    std::vector<CloseEvent> close_events;

    for (const PositionPtr& position : this->executed_positions) {
        if (!position->is_closed)
            continue;

        // Find the close index in market
        auto it = std::lower_bound(
            dates.begin(),
            dates.end(),
            position->close_date
        );
        size_t close_idx = std::distance(dates.begin(), it);
        if (close_idx >= dates.size())
            continue;

        double pnl = position->calculate_profit_and_loss();
        close_events.push_back({ close_idx, pnl });
    }

    // Sort events by index (just in case)
    std::sort(
        close_events.begin(),
        close_events.end(),
        [](const CloseEvent& a, const CloseEvent& b) {return a.time_idx < b.time_idx;}
    );

    size_t event_idx = 0;
    for (size_t i = 0; i < dates.size(); ++i) {
        while (event_idx < close_events.size() && close_events[event_idx].time_idx == i) {
            equity += close_events[event_idx].profit;
            ++event_idx;
        }
        equity_series[i] = equity;
    }

    return equity_series;
}
