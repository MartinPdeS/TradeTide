#pragma once

#include <cmath>

class RiskManagement {
public:
    double account_balance;       // Current balance of the portfolio
    double max_risk_per_trade;    // Maximum percentage of the account balance to risk per trade
    double stop_loss_distance;    // Distance (in pips) for stop-loss from the entry price
    double take_profit_distance;  // Distance (in pips) for take-profit from the entry price

public:
    // Constructor
    RiskManagement() = default;

    RiskManagement(double initial_balance, double risk_per_trade, double stop_loss, double take_profit)
        : account_balance(initial_balance), max_risk_per_trade(risk_per_trade),
          stop_loss_distance(stop_loss), take_profit_distance(take_profit) {}

    // Update account balance
    void update_balance(double new_balance);

    // Calculate position size
    double calculate_position_size(const double entry_price, const double pip_value) const;

    // Enforce risk parameters for a new position
    bool validate_position(const double entry_price, const double lot_size, const double current_price, const bool is_long) const;

    // Getters
    double get_max_risk_per_trade() const { return max_risk_per_trade; }
    double get_stop_loss_distance() const { return stop_loss_distance; }
    double get_take_profit_distance() const { return take_profit_distance; }
};
