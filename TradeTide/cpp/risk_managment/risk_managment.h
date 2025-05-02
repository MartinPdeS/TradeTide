#pragma once

#include <cmath>

class BasePosition;

class RiskManagment {
public:
    double account_balance;       // Current balance of the portfolio
    double max_risk_per_trade;    // Maximum percentage of the account balance to risk per trade
    double stop_loss;    // Distance (in pips) for stop-loss from the entry price
    double take_profit;  // Distance (in pips) for take-profit from the entry price

    // Constructor
    RiskManagment() = default;

    RiskManagment(double initial_balance, double max_risk_per_trade, double stop_loss, double take_profit)
    :
        account_balance(initial_balance),
        max_risk_per_trade(max_risk_per_trade),
        stop_loss(stop_loss),
        take_profit(take_profit) {}

    // Update account balance
    void update_balance(double new_balance);

    // Calculate position size
    double calculate_position_size(const double entry_price, const double currency_per_pip) const;
    void update_position_lot_size(BasePosition &position, const double currency_per_pip) const;

    // Enforce risk parameters for a new position
    bool validate_position(const double entry_price, const double lot_size, const double current_price, const bool is_long) const;
};
