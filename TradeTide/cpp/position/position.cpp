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



// Long Position---------------------------------------------
// Check if stop-loss or take-profit is hit
void
Long::propagate() {
    for (size_t time_idx = this->start_idx; time_idx < this->market.dates.size(); time_idx++) {
        double current_price = (*this->market.bid.price)[time_idx];

        this->exit_strategy->update_price(*this, time_idx, current_price);

        if (this->market.bid.low[time_idx] <= this->exit_strategy->stop_loss_price) {     // Hit stop-loss
            this->exit_price = this->exit_strategy->stop_loss_price;
            this->is_closed = true;
            this->close_date = this->market.dates[time_idx + 1];
            break;
        }

        if (this->market.bid.high[time_idx] >= this->exit_strategy->take_profit_price) {   // Hit take-profit
            this->exit_price = this->exit_strategy->take_profit_price;
            this->is_closed = true;
            this->close_date = this->market.dates[time_idx + 1];
            break;
        }

    }
}


// Calculate profit or loss
[[nodiscard]] double
Long::calculate_profit_and_loss() const {
    if (!is_closed)
        return 0.0; // No PnL if the position is still open

    double price_difference = exit_price - entry_price;

    return price_difference * lot_size * this->market.pip_value;
}

// Display Position Info
void
Long::display() const {
    std::cout
        << "Position Type: Long \n"
        << "Start Time: " << start_date << "\n"
        << "Stop Time: " << close_date << "\n"
        << "Entry Price: " << entry_price << "\n"
        << "Exit Price: " << (is_closed ? std::to_string(exit_price) : "N/A") << "\n"
        << "Lot Size: " << lot_size << "\n"
        << "Pip Price: " << this->market.pip_value << "\n"
        << "Position Status: " << (is_closed ? "Closed" : "Open") << "\n\n"
    ;
}




// Short Position---------------------------------------------
void
Short::propagate() {
    for (size_t time_idx = this->start_idx; time_idx < this->market.dates.size(); time_idx++) {
        double current_price = (*this->market.ask.price)[time_idx];

        this->exit_strategy->update_price(*this, time_idx, current_price);

        if (this->market.ask.high[time_idx] >= this->exit_strategy->stop_loss_price) {  // Hit stop-loss
            this->exit_price = this->exit_strategy->stop_loss_price;
            this->is_closed = true;
            this->close_date = this->market.dates[time_idx + 1];
            break;
        }

        if (this->market.ask.low[time_idx] <= this->exit_strategy->take_profit_price) {  // Hit take-profit
            this->exit_price = this->exit_strategy->take_profit_price;
            this->is_closed = true;
            this->close_date = this->market.dates[time_idx + 1];
            break;
        }
    }
}



// Calculate profit or loss
double
Short::calculate_profit_and_loss() const {
    if (!is_closed)
        return 0.0; // No PnL if the position is still open

    double price_difference = entry_price - exit_price;
    return price_difference * lot_size * this->market.pip_value;
}

// Display Position Info
void
Short::display() const {
    std::cout
        << "Position Type: Short\n"
        << "Start Time: " << start_date << "\n"
        << "Stop Time: " << close_date << "\n"
        << "Entry Price: " << entry_price << "\n"
        << "Exit Price: " << (is_closed ? std::to_string(exit_price) : "N/A") << "\n"
        << "Lot Size: " << lot_size << "\n"
        << "Pip Price: " << this->market.pip_value << "\n"
        << "Position Status: " << (is_closed ? "Closed" : "Open") << "\n\n"
    ;
}
