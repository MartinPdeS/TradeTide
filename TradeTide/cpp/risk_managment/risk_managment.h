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

        double stop_loss_price;
        double take_profit_price;

        std::vector<double> stop_loss_prices;
        std::vector<double> take_profit_prices;
        std::vector<TimePoint> dates;

        bool save_price_data = false; // Save the limit price for the position

        PipManager(const bool& save_price_data = false): save_price_data(save_price_data) {}

        virtual std::unique_ptr<PipManager> clone() const = 0;


        virtual void update_stop_loss_price(BasePosition* posistion, const double current_price);
        virtual void update_take_profit_price(BasePosition* position, const double current_price);

        virtual void start(BasePosition* position, const double entry_price);


        void update_price(BasePosition* position, const size_t time_idx, const double current_price) {
            this->update_stop_loss_price(position, current_price);
            this->update_take_profit_price(position, current_price);

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
        : PipManager(save_price_data), stop_loss(stop_loss), take_profit(take_profit) {}

        void start(BasePosition* position, const double entry_price) override {
            if (auto* long_position = dynamic_cast<Long*>(position)) {
                this->take_profit_price = entry_price + this->take_profit * position->market.pip_size;
                this->stop_loss_price = entry_price - this->stop_loss * position->market.pip_size;
            }
            else if (auto* short_position = dynamic_cast<Short*>(position)) {
                this->take_profit_price = entry_price - this->take_profit * position->market.pip_size;
                this->stop_loss_price = entry_price + this->stop_loss * position->market.pip_size;
            }
            else
                throw std::invalid_argument("Position is neither Long nor Short");
        }

        std::unique_ptr<PipManager> clone() const override {
            return std::make_unique<StaticPipManager>(*this);
        }

        void update_stop_loss_price(BasePosition* position, const double) override {
            if (auto* long_position = dynamic_cast<Long*>(position))
                this->stop_loss_price = long_position->entry_price - this->stop_loss * long_position->market.pip_size;
            else if (auto* short_position = dynamic_cast<Short*>(position))
                this->stop_loss_price = short_position->entry_price + this->stop_loss * short_position->market.pip_size;
            else
                throw std::invalid_argument("Position is neither Long nor Short");
        }

        void update_take_profit_price(BasePosition* position, const double) override {
            if (auto* long_position = dynamic_cast<Long*>(position))
                this->take_profit_price = long_position->entry_price + this->take_profit * long_position->market.pip_size;
            else if (auto* short_position = dynamic_cast<Short*>(position))
                this->take_profit_price = short_position->entry_price - this->take_profit * short_position->market.pip_size;
            else
                throw std::invalid_argument("Position is neither Long nor Short");
        }
    };


class TrailingPipManager : public PipManager {
    public:
        double stop_loss;    // Distance (in pips) for stop-loss from the entry price
        double take_profit;  // Distance (in pips) for take-profit from the entry price

        double previous_stop_loss_price; // Previous stop-loss valueà
        double previous_take_profit_price; // Previous take-profit value

        // Constructor
        TrailingPipManager() = default;

        TrailingPipManager(double stop_loss, double take_profit, const bool& save_price_data = false)
        : PipManager(save_price_data), stop_loss(stop_loss), take_profit(take_profit) {}

        void start(BasePosition* position, const double entry_price) override {
            if (auto* long_position = dynamic_cast<Long*>(position)) {
                this->take_profit_price = entry_price + this->take_profit * position->market.pip_size;
                this->stop_loss_price = entry_price - this->stop_loss * position->market.pip_size;
            }
            else if (auto* short_position = dynamic_cast<Short*>(position)) {
                this->take_profit_price = entry_price - this->take_profit * position->market.pip_size;
                this->stop_loss_price = entry_price + this->stop_loss * position->market.pip_size;
            }
            else
                throw std::invalid_argument("Position is neither Long nor Short");
        }

        std::unique_ptr<PipManager> clone() const override {
            return std::make_unique<TrailingPipManager>(*this);
        }

        void update_stop_loss_price(BasePosition* posistion, const double current_price) override {
            if (auto* long_position = dynamic_cast<Long*>(posistion)) {
                if (current_price < this->previous_take_profit_price) {
                    this->stop_loss_price = long_position->entry_price - this->stop_loss * long_position->market.pip_size;
                }
            }
            else if (auto* short_position = dynamic_cast<Short*>(posistion))
                this->stop_loss_price = short_position->entry_price + this->stop_loss * short_position->market.pip_size;
            else
                throw std::invalid_argument("Position is neither Long nor Short");
        }

        void update_take_profit_price(BasePosition* position, const double) override {
            if (auto* long_position = dynamic_cast<Long*>(position))
                this->take_profit_price = long_position->entry_price + this->take_profit * long_position->market.pip_size;
            else if (auto* short_position = dynamic_cast<Short*>(position))
                this->take_profit_price = short_position->entry_price - this->take_profit * short_position->market.pip_size;
            else
                throw std::invalid_argument("Position is neither Long nor Short");
        }

    };
