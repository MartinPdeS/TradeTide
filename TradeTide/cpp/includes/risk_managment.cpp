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
    RiskManagement(double initial_balance, double risk_per_trade, double stop_loss, double take_profit)
        : account_balance(initial_balance), max_risk_per_trade(risk_per_trade),
          stop_loss_distance(stop_loss), take_profit_distance(take_profit) {}

    // Update account balance
    void update_balance(double new_balance) {
        account_balance = new_balance;
    }

    // Calculate position size
    double calculate_position_size(double entry_price, double pip_value) const {
        // Maximum risk in dollars
        double max_risk_dollars = (max_risk_per_trade / 100.0) * account_balance;

        // Lot size based on maximum risk and stop-loss distance
        double lot_size = max_risk_dollars / (stop_loss_distance * pip_value);

        return lot_size;
    }

    // Enforce risk parameters for a new position
    bool validate_position(double entry_price, double lot_size, double current_price, bool is_long) const {
        // Calculate stop-loss and maximum risk
        double stop_loss_price = entry_price - (is_long ? stop_loss_distance : -stop_loss_distance);
        double potential_loss = abs(entry_price - stop_loss_price) * lot_size;

        return potential_loss <= (max_risk_per_trade / 100.0) * account_balance;
    }

    // Getters
    double get_max_risk_per_trade() const { return max_risk_per_trade; }
    double get_stop_loss_distance() const { return stop_loss_distance; }
    double get_take_profit_distance() const { return take_profit_distance; }
};
