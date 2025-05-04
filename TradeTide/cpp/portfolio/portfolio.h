#pragma once

#include <iostream>
#include <memory>
#include <vector>

#include "../risk_managment/risk_managment.h"
#include "../signal/signal.h"
#include "../position/position.h"

class Portfolio {
private:
    std::vector<std::shared_ptr<Position>> positions; // List of positions
    double capital;                                   // Current capital in the portfolio
    RiskManagment risk_manager;                       // Risk management instance
    size_t day;

public:
    // Constructor
    Portfolio() = default;

    Portfolio(RiskManagment& risk_manager) : risk_manager(risk_manager) {}

    // Add a new position with stop-loss and take-profit
    bool add_position(bool is_long, double entry_price, double pip_price, double lot_size, double stop_loss, double take_profit);

    // Update portfolio capital
    void update_capital(double amount);

    // Display all positions
    void display_positions() const;

    // Get current capital
    double get_capital() const { return capital; }

    // Method to get entry prices of all positions
    std::vector<double> get_entry_prices() const;

    // Method to get entry prices of all positions
    std::vector<double> get_exit_prices() const;

    // Method to get open dates of all positions
    std::vector<std::chrono::system_clock::time_point> get_open_dates() const;

    // Method to get open dates of all positions
    std::vector<std::chrono::system_clock::time_point> get_close_dates() const;
};
