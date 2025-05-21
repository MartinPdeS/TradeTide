#include <iostream>
#include <string>
#include <chrono>
#include <ctime>
#include "position.h"

#include "../exit_strategy/exit_strategy.h"


const std::vector<double>& BasePosition::strategy_stop_loss_prices() const {
    return this->exit_strategy->stop_loss_prices;
}

const std::vector<double>& BasePosition::strategy_take_profit_prices() const {
    return this->exit_strategy->take_profit_prices;
}

const std::vector<TimePoint>& BasePosition::strategy_dates() const {
    return this->exit_strategy->dates;
}


void BasePosition::terminate(const double exit_price, const size_t time_idx) {
    this->exit_price = exit_price;
    this->close_date = this->market.dates[time_idx];
    this->close_idx = time_idx;
    this->is_terminated = true;
}




// Long Position---------------------------------------------
// Check if stop-loss or take-profit is hit
void
Long::propagate() {
    for (size_t time_idx = this->open_idx; time_idx < this->market.dates.size(); time_idx++) {

        double current_price = (*this->market.bid.price)[time_idx];

        this->exit_strategy->update_price(*this, time_idx, current_price);

        if (this->market.bid.low[time_idx] <= this->exit_strategy->stop_loss_price) // Hit stop-loss
            return this->terminate(this->exit_strategy->stop_loss_price, time_idx);

        if (this->market.bid.high[time_idx] >= this->exit_strategy->take_profit_price)   // Hit take-profit
            return this->terminate(this->exit_strategy->take_profit_price, time_idx);

    }
}


// Calculate profit or loss
[[nodiscard]] double
Long::calculate_profit_and_loss() const {
    double price_difference = this->exit_price - this->entry_price;

    return price_difference * this->lot_size * this->market.pip_value;
}

// Calculate profit or loss
[[nodiscard]] double
Long::calculate_profit_and_loss_time(const size_t& time_idx) const {
    if (time_idx < this->close_idx)
        return ((*this->market.bid.price)[time_idx] - this->entry_price) * this->lot_size;

    return (this->exit_price - this->entry_price) * this->lot_size;
}

// Display Position Info
void
Long::display() const {
    std::cout
        << "Position Type: Long \n"
        << "Start Time: " << start_date << "\n"
        << "Stop Time: " << close_date << "\n"
        << "Entry Price: " << entry_price << "\n"
        << "Exit Price: " << exit_price << "\n"
        << "Lot Size: " << lot_size << "\n\n"
    ;
}




// Short Position---------------------------------------------
void
Short::propagate() {
    for (size_t time_idx = this->open_idx; time_idx < this->market.dates.size(); time_idx++) {
        double current_price = (*this->market.ask.price)[time_idx];

        this->exit_strategy->update_price(*this, time_idx, current_price);

        if (this->market.ask.high[time_idx] >= this->exit_strategy->stop_loss_price)  // Hit stop-loss
            return this->terminate(this->exit_strategy->stop_loss_price, time_idx);
            this->exit_price = this->exit_strategy->stop_loss_price;

        if (this->market.ask.low[time_idx] <= this->exit_strategy->take_profit_price)  // Hit take-profit
            return this->terminate(this->exit_strategy->take_profit_price, time_idx);
    }
}



// Calculate profit or loss
double
Short::calculate_profit_and_loss() const {
    double price_difference = this->entry_price - this->exit_price;

    return price_difference * this->lot_size * this->market.pip_value;
}

// Calculate profit or loss
[[nodiscard]] double
Short::calculate_profit_and_loss_time(const size_t& time_idx) const {
    if (time_idx < this->open_idx)
        return 0.0; // No PnL if the position is still open

    if (time_idx < this->close_idx)
        return ((*this->market.ask.price)[time_idx] - this->entry_price) * this->lot_size;

    return (this->exit_price - this->entry_price) * this->lot_size;
}

// Display Position Info
void
Short::display() const {
    std::cout
        << "Position Type: Short\n"
        << "Start Time: " << start_date << "\n"
        << "Stop Time: " << close_date << "\n"
        << "Entry Price: " << entry_price << "\n"
        << "Exit Price: " << exit_price<< "\n"
        << "Lot Size: " << lot_size << "\n\n"
    ;
}
