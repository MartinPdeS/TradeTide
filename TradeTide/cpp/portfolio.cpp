#pragma once

#include <vector>
#include <iostream>
#include <memory>
#include "position.cpp"
#include "risk_managment.cpp"
#include "signal.cpp"

class Portfolio {
private:
    std::vector<std::shared_ptr<Position>> positions; // List of positions
    double capital;                                   // Current capital in the portfolio
    RiskManagement risk_manager;                     // Risk management instance

public:
    // Constructor
    Portfolio(RiskManagement& risk_manager)
        : capital(risk_manager.account_balance), risk_manager(risk_manager) {}

    // Add a new position with stop-loss and take-profit
    bool add_position(bool is_long, double entry_price, double pip_price, double lot_size, double stop_loss, double take_profit) {
        double lot_size_calculated = risk_manager.calculate_position_size(entry_price, pip_price);
        if (lot_size_calculated <= 0) {
            std::cerr << "Invalid lot size calculated. Position not added.\n";
            return false;
        }

        auto position = std::make_shared<Position>(is_long, entry_price, lot_size, pip_price, stop_loss, take_profit);
        positions.push_back(position);
        position->open(entry_price); // Open the position
        return true;
    }

    // Check and close positions hitting stop-loss or take-profit
    void check_exit_conditions(const Market& market, size_t day_index) {
        double high_price = market.get_high_prices()[day_index];
        double low_price = market.get_low_prices()[day_index];

        for (auto& position : positions) {
            if (!position->get_is_closed() && position->check_exit_conditions(high_price, low_price)) {
                double pnl = position->calculate_pnl();
                update_capital(pnl);
                std::cout << "Position closed with PnL: " << pnl << " USD\n";
            }
        }
    }

    // Process signals and execute trades
    void process_signals(const Signal& signal, const Market& market, double pip_price, double stop_loss_offset, double take_profit_offset) {
        const auto& signal_array = signal.get_signals();
        const auto& close_prices = market.get_close_prices();

        std::cout << "Processing signals...\n";

        for (size_t i = 0; i < signal_array.size(); ++i) {
            // Check for exit conditions
            check_exit_conditions(market, i);

            // Handle new signals
            if (signal_array[i] == 1) {
                add_position(true, close_prices[i], pip_price, 1.0, close_prices[i] - stop_loss_offset, close_prices[i] + take_profit_offset);
                std::cout << "Day " << i + 1 << ": Executed Buy at price " << close_prices[i] << "\n";
            } else if (signal_array[i] == -1) {
                add_position(false, close_prices[i], pip_price, 1.0, close_prices[i] + stop_loss_offset, close_prices[i] - take_profit_offset);
                std::cout << "Day " << i + 1 << ": Executed Sell at price " << close_prices[i] << "\n";
            } else {
                std::cout << "Day " << i + 1 << ": No action.\n";
            }
        }
    }

    // Update portfolio capital
    void update_capital(double amount) {
        capital += amount;
        risk_manager.update_balance(capital);
    }

    // Display all positions
    void display_positions() const {
        std::cout << "Portfolio Positions:\n";
        for (const auto& position : positions) {
            position->display();
            std::cout << "-----------------------\n";
        }
        std::cout << "Current Capital: " << capital << " USD\n";
    }

    // Get current capital
    double get_capital() const { return capital; }
};
