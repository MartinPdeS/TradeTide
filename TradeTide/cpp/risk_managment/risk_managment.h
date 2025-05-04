#pragma once

#include <cmath>

class BasePosition;

class RiskManagment {
public:
    double stop_loss;    // Distance (in pips) for stop-loss from the entry price
    double take_profit;  // Distance (in pips) for take-profit from the entry price

    // Constructor
    RiskManagment() = default;

    RiskManagment(double stop_loss, double take_profit)
    :
        stop_loss(stop_loss),
        take_profit(take_profit) {}

    // Update account balance
    void update_balance(double new_balance);

    // Calculate position size
    double calculate_position_size(const double entry_price, const double currency_per_pip) const;
    void update_position_lot_size(BasePosition &position, const double currency_per_pip) const;

    // Enforce risk parameters for a new position
    bool validate_position(const double entry_price, const double lot_size, const double current_price, const bool is_long) const;


    const double& get_stop_loss() const {
        return this->stop_loss;
    }

    const double& get_take_profit() const {
        return this->take_profit;
    }
};


class PipManager {
public:
    virtual ~PipManager() = default;

    // Pure virtual functions to be implemented by derived classes
    virtual const double& get_stop_loss(const double& price) = 0;
    virtual const double& get_take_profit(const double& price) = 0;

};

class StaticPipManager : PipManager {
    public:
        double stop_loss;    // Distance (in pips) for stop-loss from the entry price
        double take_profit;  // Distance (in pips) for take-profit from the entry price

        // Constructor
        StaticPipManager() = default;

        StaticPipManager(double stop_loss, double take_profit)
        :
            stop_loss(stop_loss),
            take_profit(take_profit) {}

        const double& get_stop_loss(const double& price) {
            return this->stop_loss;
        }

        const double& get_take_profit(const double& price) {
            return this->take_profit;
        }
    };


class TrailingPipManager : PipManager {
    public:
        double stop_loss;    // Distance (in pips) for stop-loss from the entry price
        double take_profit;  // Distance (in pips) for take-profit from the entry price

        double previous_stop_loss; // Previous stop-loss valueà
        double previous_take_profit; // Previous take-profit value
        double trailing_stop_loss; // Trailing stop-loss value
        double trailing_take_profit; // Trailing take-profit value


        // Constructor
        TrailingPipManager() = default;

        TrailingPipManager(double stop_loss, double take_profit)
        :
            stop_loss(stop_loss),
            take_profit(take_profit) {}

        const double& get_stop_loss(const double& price) {
            if (price > this->previous_stop_loss) {
                this->trailing_stop_loss = price - stop_loss;
                this->previous_stop_loss = trailing_stop_loss;
            }
            return trailing_stop_loss;
        }

        const double& get_take_profit(const double& price) {
            if (price < this->previous_take_profit) {
                this->trailing_take_profit = price + take_profit;
                this->previous_take_profit = trailing_take_profit;
            }
            return trailing_take_profit;
        }
    };
