#include <iostream>
#include <string>
#include <chrono>
#include <ctime>
#include "position.h"

#include "../risk_managment/risk_managment.h"

// Open Position
void
Position::open(double price) {
    entry_price = price;
    is_closed = false;
    start_date = std::chrono::system_clock::now();
}

// Close the position and calculate profit or loss
void
Position::close(double market_price) {
    if (!is_closed) {
        exit_price = market_price;
        is_closed = true;
        close_date = std::chrono::system_clock::now();
    }
}

// Check if stop-loss or take-profit is hit
bool
Position::check_exit_conditions(const double high_price, const double low_price) {
    if (is_closed) return false;

    if (is_long) {
        if (low_price <= stop_loss) {
            this->close(stop_loss); // Hit stop-loss
            return true;
        }
        if (high_price >= take_profit) {
            this->close(take_profit); // Hit take-profit
            return true;
        }
    } else {
        if (high_price >= stop_loss) {
            this->close(stop_loss); // Hit stop-loss
            return true;
        }
        if (low_price <= take_profit) {
            this->close(take_profit); // Hit take-profit
            return true;
        }
    }
    return false;
}

// Calculate profit or loss
double
Position::calculate_profite_and_loss() const {
    if (!is_closed) return 0.0; // No PnL if the position is still open

    double price_difference = is_long ? (exit_price - entry_price) : (entry_price - exit_price);
    return price_difference * lot_size * pip_price;
}

// Display Position Info
void
Position::display() const {
    std::cout
        << "Position Type: " << (is_long ? "Long" : "Short") << "\n"
        << "Entry Price: " << entry_price << "\n"
        << "Exit Price: " << (is_closed ? std::to_string(exit_price) : "N/A") << "\n"
        << "Stop Loss: " << stop_loss << "\n"
        << "Take Profit: " << take_profit << "\n"
        << "Lot Size: " << lot_size << "\n"
        << "Pip Price: " << pip_price << "\n"
        << "Position Status: " << (is_closed ? "Closed" : "Open") << "\n"
    ;
}



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
    if (!this->is_closed) {
        this->exit_price = (*this->market.bid.price)[time_idx];
        this->is_closed = true;
        this->close_date = this->market.dates[time_idx];
    }
}

void
Long::close_stop_loss(const size_t time_idx) {
    if (this-is_closed)
        return;

    double price = (*this->market.bid.price)[time_idx];
    double stop_loss = this->risk_managment.get_stop_loss(price);

    this->exit_price = (*this->market.bid.price)[time_idx] - this->risk_managment.stop_loss;
    this->is_closed = true;
    this->close_date = this->market.dates[time_idx];

}

void
Long::close_take_profit(const size_t time_idx) {
    if (!this->is_closed) {
        this->exit_price = (*this->market.bid.price)[time_idx] + this->risk_managment.take_profit;
        this->is_closed = true;
        this->close_date = this->market.dates[time_idx];
    }
}




void
Long::check_exit_conditions(const size_t time_idx) {
    if (is_closed)
        return;

    if (this->market.bid.low[time_idx] <= this->entry_price - this->risk_managment.stop_loss * 1e-4) {    // Hit stop-loss
        this->close_stop_loss(time_idx);
        return;
    }
    if (this->market.bid.high[time_idx] >= this->entry_price + this->risk_managment.take_profit * 1e-4) {  // Hit take-profit
        this->close_take_profit(time_idx);
        return;
    }

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
        << "Stop Loss: " << this->risk_managment.stop_loss << "\n"
        << "Take Profit: " << this->risk_managment.take_profit << "\n"
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
    if (!this->is_closed) {
        this->exit_price = (*this->market.ask.price)[time_idx] + this->risk_managment.stop_loss;
        this->is_closed = true;
        this->close_date = this->market.dates[time_idx];
    }
}

void
Short::close_take_profit(const size_t time_idx) {
    if (!this->is_closed) {
        this->exit_price = (*this->market.ask.price)[time_idx] - this->risk_managment.take_profit;
        this->is_closed = true;
        this->close_date = this->market.dates[time_idx];
    }
}


// Check if stop-loss or take-profit is hit
void
Short::check_exit_conditions(const size_t time_idx) {
    if (is_closed)
        return;

    if (this->market.ask.high[time_idx] >= this->entry_price + this->risk_managment.stop_loss * 1e-4) {  // Hit stop-loss
        this->close_stop_loss(time_idx);
        return;
    }

    if (this->market.ask.low[time_idx] <= this->entry_price - this->risk_managment.take_profit * 1e-4) {  // Hit take-profit
        this->close_take_profit(time_idx);
        return;
    }
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
        << "Stop Loss: " << this->risk_managment.stop_loss << "\n"
        << "Take Profit: " << this->risk_managment.take_profit << "\n"
        << "Lot Size: " << lot_size << "\n"
        << "Pip Price: " << this->market.pip_value << "\n"
        << "Position Status: " << (is_closed ? "Closed" : "Open") << "\n\n"
    ;
}
