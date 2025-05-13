#pragma once

#include <cmath>
#include <memory>
#include <vector>

#include "../market/market.h"
#include "../position/position.h"

using TimePoint = std::chrono::system_clock::time_point;

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

        double stop_loss_price;
        double take_profit_price;

        std::vector<double> stop_loss_prices;
        std::vector<double> take_profit_prices;
        std::vector<TimePoint> dates;

        bool save_price_data = false; // Save the limit price for the position

        PipManager(const bool& save_price_data = false): save_price_data(save_price_data) {}

        // Pure virtual functions to be implemented by derived classes
        virtual double& get_stop_loss(const double& price) = 0;
        virtual double& get_take_profit(const double& price) = 0;

        virtual std::unique_ptr<PipManager> clone() const = 0;


        void update_stop_loss_price(BasePosition* pos) {
            double _stop_loss = this->get_stop_loss(pos->entry_price);

            if (auto* long_position = dynamic_cast<Long*>(pos))
                this->stop_loss_price = long_position->entry_price - _stop_loss * long_position->market.pip_size;
            else if (auto* short_position = dynamic_cast<Short*>(pos))
                this->stop_loss_price = short_position->entry_price + _stop_loss * short_position->market.pip_size;
            else
                throw std::invalid_argument("Position is neither Long nor Short");
        }

        void update_take_profit_price(BasePosition* position) {
            double _take_profit = this->get_take_profit(position->entry_price);

            if (auto* long_position = dynamic_cast<Long*>(position))
                this->take_profit_price = long_position->entry_price + _take_profit * long_position->market.pip_size;
            else if (auto* short_position = dynamic_cast<Short*>(position))
                this->take_profit_price = short_position->entry_price - _take_profit * short_position->market.pip_size;
            else
                throw std::invalid_argument("Position is neither Long nor Short");
        }

        void update_price(BasePosition* position, const size_t time_idx) {
            this->update_stop_loss_price(position);
            this->update_take_profit_price(position);

            if (this->save_price_data) {
                this->dates.push_back(position->market.dates[time_idx]);
                this->stop_loss_prices.push_back(this->stop_loss_price);
                this->take_profit_prices.push_back(this->take_profit_price);
            }
        }
};

class StaticPipManager : public PipManager {
    public:
        double stop_loss;    // Distance (in pips) for stop-loss from the entry price
        double take_profit;  // Distance (in pips) for take-profit from the entry price

        // Constructor
        StaticPipManager() = default;

        StaticPipManager(double stop_loss, double take_profit, const bool& save_price_data = false)
        :
            PipManager(save_price_data),
            stop_loss(stop_loss),
            take_profit(take_profit)
             {}

        double& get_stop_loss(const double&) override {
            return this->stop_loss;
        }

        double& get_take_profit(const double&) override {
            return this->take_profit;
        }

        std::unique_ptr<PipManager> clone() const override {
            return std::make_unique<StaticPipManager>(*this);
        }
    };


class TrailingPipManager : public PipManager {
    public:
        double stop_loss;    // Distance (in pips) for stop-loss from the entry price
        double take_profit;  // Distance (in pips) for take-profit from the entry price

        double previous_stop_loss; // Previous stop-loss valueà
        double previous_take_profit; // Previous take-profit value
        double trailing_stop_loss; // Trailing stop-loss value
        double trailing_take_profit; // Trailing take-profit value

        // Constructor
        TrailingPipManager() = default;

        TrailingPipManager(double stop_loss, double take_profit, const bool& save_price_data = false)
        :
        PipManager(save_price_data),
            stop_loss(stop_loss),
            take_profit(take_profit),
            trailing_stop_loss(stop_loss),
            trailing_take_profit(take_profit){}

        double& get_stop_loss(const double& price) override {
            if (price > this->previous_stop_loss) {
                this->trailing_stop_loss = price - stop_loss;
                this->previous_stop_loss = this->trailing_stop_loss;
            }
            return this->trailing_stop_loss;
        }

        double& get_take_profit(const double& price) override {
            if (price < this->previous_take_profit) {
                this->trailing_take_profit = price + take_profit;
                this->previous_take_profit = this->trailing_take_profit;
            }
            return this->trailing_take_profit;
        }
        std::unique_ptr<PipManager> clone() const override {
            return std::make_unique<TrailingPipManager>(*this);
        }
    };
