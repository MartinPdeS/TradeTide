#include <iostream>
#include <string>
#include <chrono>
#include <ctime>

class Position {
private:
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
    Position(bool long_position, double price, double lots, double pip_val, double stop, double profit)
        : is_long(long_position), entry_price(price), lot_size(lots), pip_price(pip_val),
          stop_loss(stop), take_profit(profit), exit_price(0.0), is_closed(false) {}

    // Open Position
    void open(double price) {
        entry_price = price;
        is_closed = false;
        start_time = std::chrono::system_clock::now();
    }

    // Close the position and calculate profit or loss
    void close(double market_price) {
        if (!is_closed) {
            exit_price = market_price;
            is_closed = true;
            close_time = std::chrono::system_clock::now();
        }
    }

    // Check if stop-loss or take-profit is hit
    bool check_exit_conditions(double high_price, double low_price) {
        if (is_closed) return false;

        if (is_long) {
            if (low_price <= stop_loss) {
                close(stop_loss); // Hit stop-loss
                return true;
            }
            if (high_price >= take_profit) {
                close(take_profit); // Hit take-profit
                return true;
            }
        } else {
            if (high_price >= stop_loss) {
                close(stop_loss); // Hit stop-loss
                return true;
            }
            if (low_price <= take_profit) {
                close(take_profit); // Hit take-profit
                return true;
            }
        }
        return false;
    }

    // Calculate profit or loss
    double calculate_pnl() const {
        if (!is_closed) return 0.0; // No PnL if the position is still open

        double price_difference = is_long ? (exit_price - entry_price) : (entry_price - exit_price);
        return price_difference * lot_size * pip_price;
    }

    // Display Position Info
    void display() const {
        std::cout << "Position Type: " << (is_long ? "Long" : "Short") << "\n"
                  << "Entry Price: " << entry_price << "\n"
                  << "Exit Price: " << (is_closed ? std::to_string(exit_price) : "N/A") << "\n"
                  << "Stop Loss: " << stop_loss << "\n"
                  << "Take Profit: " << take_profit << "\n"
                  << "Lot Size: " << lot_size << "\n"
                  << "Pip Price: " << pip_price << "\n"
                  << "Position Status: " << (is_closed ? "Closed" : "Open") << "\n";
    }

    bool get_is_closed() const { return is_closed; }
};
