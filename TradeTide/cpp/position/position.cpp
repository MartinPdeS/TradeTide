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
Position::calculate_pnl() const {
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






// Base Position---------------------------------------------
void
BasePosition::open(const double price) {
    entry_price = price;
    is_closed = false;
    start_date = std::chrono::system_clock::now();
}

// Close the position and calculate profit or loss
void
BasePosition::close(const double market_price) {
    if (!is_closed) {
        exit_price = market_price;
        is_closed = true;
        close_date = std::chrono::system_clock::now();
    }
}




// Long Position---------------------------------------------
// Check if stop-loss or take-profit is hit
void
Long::check_exit_conditions(const size_t time_idx) {
    if (is_closed)
        return;

    if (this->market.low_prices[time_idx] <= this->risk_managment.stop_loss_distance) {    // Hit stop-loss
        this->close(this->risk_managment.stop_loss_distance);
        this->close_date = this->market.dates[time_idx];
    }
    if (this->market.high_prices[time_idx] >= this->risk_managment.take_profit_distance) {  // Hit take-profit
        this->close(this->risk_managment.take_profit_distance);
        this->close_date = this->market.dates[time_idx];
    }

}

// Calculate profit or loss
double
Long::calculate_pnl() const {
    if (!is_closed)
        return 0.0; // No PnL if the position is still open

    double price_difference = exit_price - entry_price;
    return price_difference * lot_size * pip_price;
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
        << "Stop Loss: " << this->risk_managment.stop_loss_distance << "\n"
        << "Take Profit: " << this->risk_managment.take_profit_distance << "\n"
        << "Lot Size: " << lot_size << "\n"
        << "Pip Price: " << pip_price << "\n"
        << "Position Status: " << (is_closed ? "Closed" : "Open") << "\n\n"
    ;
}




// Short Position---------------------------------------------

// Check if stop-loss or take-profit is hit
void
Short::check_exit_conditions(const size_t time_idx) {
    if (is_closed)
        return;

    if (this->market.high_prices[time_idx] >= this->risk_managment.stop_loss_distance) {  // Hit stop-loss
        this->close(this->risk_managment.stop_loss_distance);
        this->close_date = this->market.dates[time_idx];


    }
    if (this->market.low_prices[time_idx] <= this->risk_managment.take_profit_distance) {  // Hit take-profit
        this->close(this->risk_managment.take_profit_distance);
        this->close_date = this->market.dates[time_idx];
    }
}

// Calculate profit or loss
double
Short::calculate_pnl() const {
    if (!is_closed)
        return 0.0; // No PnL if the position is still open

    double price_difference = entry_price - exit_price;
    return price_difference * lot_size * pip_price;
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
        << "Stop Loss: " << this->risk_managment.stop_loss_distance << "\n"
        << "Take Profit: " << this->risk_managment.take_profit_distance << "\n"
        << "Lot Size: " << lot_size << "\n"
        << "Pip Price: " << pip_price << "\n"
        << "Position Status: " << (is_closed ? "Closed" : "Open") << "\n\n"
    ;
}
