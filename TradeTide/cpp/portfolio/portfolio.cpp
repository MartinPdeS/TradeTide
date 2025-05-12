#include "portfolio.h"


// Add a new position with stop-loss and take-profit
bool
Portfolio::add_position(bool is_long, double entry_price, double pip_price, double lot_size, double stop_loss, double take_profit)
    {
        // Validate and calculate lot size based on risk management
        double lot_size_calculated = risk_manager.calculate_position_size(entry_price, pip_price);
        if (lot_size_calculated <= 0) {
            std::cerr << "Invalid lot size calculated. Position not added.\n";
            return false;
        }

        std::cout << "Day " << day + 1 << ": Executed open position at price " << entry_price << "is long: "<< is_long << "\n";

        // Create and open a new position with stop-loss and take-profit
        auto position = std::make_shared<BasePosition>(is_long, entry_price, lot_size, pip_price, stop_loss, take_profit);
        positions.push_back(position);
        // position->open(entry_price);
        return true;
}




// Update portfolio capital
void
Portfolio::update_capital(double amount) {
    capital += amount;
    risk_manager.update_balance(capital);
}

// Display all positions
void
Portfolio::display_positions() const {
    std::cout << "Portfolio Positions:\n";
    for (const auto& position : positions) {
        position->display();
        std::cout << "-----------------------\n";
    }
    std::cout << "Current Capital: " << capital << " USD\n";
}

// Method to get entry prices of all positions
std::vector<double>
Portfolio::get_entry_prices() const {
    std::vector<double> entry_prices;
    for (const auto& position : positions) {
        entry_prices.push_back(position->entry_price);
    }
    return entry_prices;
}

// Method to get entry prices of all positions
std::vector<double>
Portfolio::get_exit_prices() const {
    std::vector<double> exit_prices;
    for (const auto& position : positions) {
        exit_prices.push_back(position->exit_price);
    }
    return exit_prices;
}


// Method to get open dates of all positions
std::vector<std::chrono::system_clock::time_point>
Portfolio::get_open_dates() const {
    std::vector<std::chrono::system_clock::time_point> open_dates;
    for (const auto& position : positions) {
        open_dates.push_back(position->start_date);
    }
    return open_dates;
}


// Method to get open dates of all positions
std::vector<std::chrono::system_clock::time_point>
Portfolio::get_close_dates() const {
    std::vector<std::chrono::system_clock::time_point> close_dates;
    for (const auto& position : positions) {
        close_dates.push_back(position->start_date);
    }
    return close_dates;
}

