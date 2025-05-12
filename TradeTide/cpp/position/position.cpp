#include <iostream>
#include <string>
#include <chrono>
#include <ctime>
#include "position.h"

#include "../risk_managment/risk_managment.h"


// Long Position---------------------------------------------
// Check if stop-loss or take-profit is hit
void
Long::open(const size_t time_idx) {
    entry_price = (*this->market.ask.price)[time_idx];
    is_closed = false;
    start_date = this->market.dates[time_idx];
}


void
Long::close(const size_t time_idx) {
    if (this-is_closed)
        return;

    this->exit_price = (*this->market.bid.price)[time_idx];
    this->is_closed = true;
    this->close_date = this->market.dates[time_idx];

}

void
Long::close_stop_loss(const size_t time_idx) {
    if (this->is_closed)
        return;

    double price = (*this->market.bid.price)[time_idx];
    double stop_loss = this->risk_managment.get_stop_loss(price);

    this->exit_price = price - stop_loss;
    this->is_closed = true;
    this->close_date = this->market.dates[time_idx];

}

void
Long::close_take_profit(const size_t time_idx) {
    if (this->is_closed)
        return;

    double take_profit = this->risk_managment.get_take_profit(this->entry_price);


    this->exit_price = (*this->market.bid.price)[time_idx] + take_profit;
    this->is_closed = true;
    this->close_date = this->market.dates[time_idx];

}




void
Long::check_exit_conditions(const size_t time_idx) {
    if (is_closed)
        return;

    double stop_loss = this->risk_managment.get_stop_loss(this->entry_price);

    if (this->market.bid.low[time_idx] <= this->entry_price - stop_loss * this->market.pip_size)     // Hit stop-loss
        return this->close_stop_loss(time_idx);


    double take_profit = this->risk_managment.get_take_profit(this->entry_price);

    if (this->market.bid.high[time_idx] >= this->entry_price + take_profit * this->market.pip_size)   // Hit take-profit
        return this->close_take_profit(time_idx);


}

// Calculate profit or loss
double
Long::calculate_profite_and_loss() const {
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
Short::open(const size_t time_idx) {
    entry_price = (*this->market.bid.price)[time_idx];
    is_closed = false;
    start_date = this->market.dates[time_idx];
}

void
Short::close(const size_t time_idx) {
    if (!is_closed) {
        exit_price = (*this->market.ask.price)[time_idx];
        is_closed = true;
        close_date = this->market.dates[time_idx];
    }
}

void
Short::close_stop_loss(const size_t time_idx) {
    if (this->is_closed)
        return;

    double stop_loss = this->risk_managment.get_stop_loss(this->entry_price);

    this->exit_price = (*this->market.ask.price)[time_idx] + stop_loss;
    this->is_closed = true;
    this->close_date = this->market.dates[time_idx];

}

void
Short::close_take_profit(const size_t time_idx) {
    if (this->is_closed)
        return;


    double take_profit = this->risk_managment.get_take_profit(this->entry_price);

    this->exit_price = (*this->market.ask.price)[time_idx] - take_profit;
    this->is_closed = true;
    this->close_date = this->market.dates[time_idx];

}


// Check if stop-loss or take-profit is hit
void
Short::check_exit_conditions(const size_t time_idx) {
    if (is_closed)
        return;

    double stop_loss = this->risk_managment.get_stop_loss(this->entry_price);

    if (this->market.ask.high[time_idx] >= this->entry_price + stop_loss * this->market.pip_size)  // Hit stop-loss
        return this->close_stop_loss(time_idx);


    double take_profit = this->risk_managment.get_take_profit(this->entry_price);

    if (this->market.ask.low[time_idx] <= this->entry_price - take_profit * this->market.pip_size)  // Hit take-profit
        return this->close_take_profit(time_idx);

}

// Calculate profit or loss
double
Short::calculate_profite_and_loss() const {
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
