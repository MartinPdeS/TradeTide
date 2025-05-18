#pragma once

#include <cmath>
#include <memory>
#include <vector>

#include "../market/market.h"
#include "../position/position.h"

using TimePoint = std::chrono::system_clock::time_point;

class BasePosition;


class PipManager {
    public:
        virtual ~PipManager() = default;

        double stop_loss_price = 0;
        double take_profit_price = 0;

        std::vector<double> stop_loss_prices;
        std::vector<double> take_profit_prices;
        std::vector<TimePoint> dates;

        bool save_price_data = false; // Save the limit price for the position

        PipManager(const bool& save_price_data = false): save_price_data(save_price_data) {}

        virtual std::unique_ptr<PipManager> clone() const = 0;

        virtual void update_stop_loss_price(BasePosition& posistion, const double &current_price) = 0;
        virtual void update_take_profit_price(BasePosition& position, const double &current_price) = 0;


        void update_price(BasePosition& position, const size_t time_idx, const double &current_price) {
            this->update_stop_loss_price(position, current_price);
            this->update_take_profit_price(position, current_price);

            if (this->save_price_data) {
                this->dates.push_back(position.market.dates[time_idx]);
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
        : PipManager(save_price_data), stop_loss(stop_loss), take_profit(take_profit) {}

        std::unique_ptr<PipManager> clone() const override {
            return std::make_unique<StaticPipManager>(*this);
        }

        void update_stop_loss_price(BasePosition& position, const double&) override {
            if (position.is_long)
                this->stop_loss_price = position.entry_price - this->stop_loss * position.market.pip_size;
            else
                this->stop_loss_price = position.entry_price + this->stop_loss * position.market.pip_size;
        }

        void update_take_profit_price(BasePosition& position, const double&) override {
            if (position.is_long)
                this->take_profit_price = position.entry_price + this->take_profit * position.market.pip_size;
            else
                this->take_profit_price = position.entry_price - this->take_profit * position.market.pip_size;
        }
    };


class TrailingPipManager : public PipManager {
    public:
        double stop_loss;    // Distance (in pips) for stop-loss from the entry price
        double take_profit;  // Distance (in pips) for take-profit from the entry price


        // Constructor
        TrailingPipManager() = default;

        TrailingPipManager(double stop_loss, double take_profit, const bool& save_price_data = false)
        : PipManager(save_price_data), stop_loss(stop_loss), take_profit(take_profit) {}

        std::unique_ptr<PipManager> clone() const override {
            return std::make_unique<TrailingPipManager>(*this);
        }

        void update_stop_loss_price(BasePosition& position, const double& current_price) override {
            if (position.is_long) {
                double current_stop_loss_price = current_price - this->stop_loss * position.market.pip_size;

                if (this->stop_loss_price == 0)
                    this->stop_loss_price = current_stop_loss_price;

                if (current_stop_loss_price > this->stop_loss_price)
                    this->stop_loss_price = current_stop_loss_price;
            }
            else {
                double current_stop_loss_price = current_price + this->stop_loss * position.market.pip_size;

                if (this->stop_loss_price == 0)
                    this->stop_loss_price = current_stop_loss_price;

                if (current_stop_loss_price < this->stop_loss_price)
                    this->stop_loss_price = current_stop_loss_price;
            }
        }

        void update_take_profit_price(BasePosition& position, const double& current_price) override {
            if (position.is_long) {
                double current_take_profit_price = current_price + this->take_profit * position.market.pip_size;

                if (this->take_profit_price == 0)
                    this->take_profit_price = current_take_profit_price;

                if (current_take_profit_price < this->take_profit_price)
                    this->take_profit_price = current_take_profit_price;
            }
            else {
                double current_take_profit_price = current_price - this->take_profit * position.market.pip_size;

                if (this->take_profit_price == 0)
                    this->take_profit_price = current_take_profit_price;

                if (current_take_profit_price > this->take_profit_price)
                    this->take_profit_price = current_take_profit_price;
            }
        }

    };
