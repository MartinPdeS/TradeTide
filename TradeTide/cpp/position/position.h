#pragma once

#include <string>
#include <chrono>
#include <ctime>

class Position {
public:
    bool is_long;              // true for long, false for short
    double entry_price;        // Price at which the position is opened
    double exit_price;         // Price at which the position is closed
    double lot_size;           // Size of the position in lots
    double pip_price;          // Pip value for the position
    double stop_loss;          // Stop-loss price level
    double take_profit;        // Take-profit price level
    bool is_closed;            // Status of the position
    std::chrono::system_clock::time_point start_time; // Time when position was opened
    std::chrono::system_clock::time_point close_time; // Time when position was closed

public:
    // Constructor
    Position() = default;

    Position(bool long_position, double price, double lots, double pip_val, double stop_loss, double take_profit)
        : is_long(long_position), entry_price(price), exit_price(0.0), lot_size(lots), pip_price(pip_val),
          stop_loss(stop_loss), take_profit(take_profit), is_closed(false) {}

    // Open Position
    void open(double price);

    // Close the position and calculate profit or loss
    void close(double market_price);

    // Check if stop-loss or take-profit is hit
    bool check_exit_conditions(double high_price, double low_price);

    // Calculate profit or loss
    double calculate_pnl() const;

    // Display Position Info
    void display() const;

    bool get_is_closed() const;
};
