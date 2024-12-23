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
    size_t day;
public:
    // Constructor
    Portfolio(RiskManagement& risk_manager)
        : capital(risk_manager.account_balance), risk_manager(risk_manager) {}

    // Add a new position with stop-loss and take-profit
    bool add_position(bool is_long, double entry_price, double pip_price,
        double lot_size, double stop_loss, double take_profit)
        {
            // Validate and calculate lot size based on risk management
            double lot_size_calculated = risk_manager.calculate_position_size(entry_price, pip_price);
            if (lot_size_calculated <= 0) {
                std::cerr << "Invalid lot size calculated. Position not added.\n";
                return false;
            }

            std::cout << "Day " << day + 1 << ": Executed open position at price " << entry_price << "is long: "<< is_long << "\n";

            // Create and open a new position with stop-loss and take-profit
            auto position = std::make_shared<Position>(is_long, entry_price, lot_size, pip_price, stop_loss, take_profit);
            positions.push_back(position);
            position->open(entry_price);
            return true;
    }

    // Check and close positions hitting stop-loss or take-profit
    void check_exit_conditions(const Market& market, size_t day_index) {
        // Get high and low prices for the current day
        double high_price = market.get_high_prices()[day_index];
        double low_price = market.get_low_prices()[day_index];

        for (auto& position : positions) {
            // Check if the position hits stop-loss or take-profit
            if (!position->get_is_closed() && position->check_exit_conditions(high_price, low_price)) {
                // Calculate profit or loss and update portfolio capital
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

        day = 0;
        for (size_t day = 0; day < signal_array.size(); ++day) {
            // Check for positions hitting stop-loss or take-profit
            check_exit_conditions(market, day);

            // Handle new signals for opening positions
            if (signal_array[day] == 1) // Open a long position with calculated stop-loss and take-profit
                add_position(true, close_prices[day], pip_price, 1.0, close_prices[day] - stop_loss_offset, close_prices[day] + take_profit_offset);
            else if (signal_array[day] == -1) // Open a short position with calculated stop-loss and take-profit
                add_position(false, close_prices[day], pip_price, 1.0, close_prices[day] + stop_loss_offset, close_prices[day] - take_profit_offset);


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


    // Method to get entry prices of all positions
    std::vector<double> get_entry_prices() const {
        std::vector<double> entry_prices;
        for (const auto& position : positions) {
            entry_prices.push_back(position->entry_price);
        }
        return entry_prices;
    }

    // Method to get entry prices of all positions
    std::vector<double> get_exit_prices() const {
        std::vector<double> exit_prices;
        for (const auto& position : positions) {
            exit_prices.push_back(position->exit_price);
        }
        return exit_prices;
    }


    // Method to get open dates of all positions
    std::vector<std::chrono::system_clock::time_point> get_open_dates() const {
        std::vector<std::chrono::system_clock::time_point> open_dates;
        for (const auto& position : positions) {
            open_dates.push_back(position->start_time);
        }
        return open_dates;
    }


    // Method to get open dates of all positions
    std::vector<std::chrono::system_clock::time_point> get_close_dates() const {
        std::vector<std::chrono::system_clock::time_point> close_dates;
        for (const auto& position : positions) {
            close_dates.push_back(position->start_time);
        }
        return close_dates;
    }
};
