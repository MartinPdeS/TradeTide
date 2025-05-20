#pragma once

#include <cmath>
#include <memory>
#include <vector>

#include "../market/market.h"
#include "../position/position.h"

using TimePoint = std::chrono::system_clock::time_point;
using Duration = std::chrono::system_clock::duration;

class BasePosition;


class ExitStrategy {
    public:
        virtual ~ExitStrategy() = default;

        double stop_loss_pip;    // Distance (in pips) for stop-loss from the entry price
        double take_profit_pip;  // Distance (in pips) for take-profit from the entry price


        double stop_loss_price = 0;
        double take_profit_price = 0;

        std::vector<double> stop_loss_prices;
        std::vector<double> take_profit_prices;
        std::vector<TimePoint> dates;

        bool save_price_data = false; // Save the limit price for the position

        ExitStrategy(const double stop_loss_pip, const double take_profit_pip, const bool& save_price_data = false)
        : stop_loss_pip(stop_loss_pip), take_profit_pip(take_profit_pip), save_price_data(save_price_data) {}

        virtual std::unique_ptr<ExitStrategy> clone() const = 0;

        virtual void update_stop_loss_price(BasePosition& position, const double &current_price) = 0;
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

class StaticExitStrategy : public ExitStrategy {
    public:

        StaticExitStrategy(double stop_loss_pip, double take_profit_pip, const bool& save_price_data = false)
        : ExitStrategy(stop_loss_pip, take_profit_pip, save_price_data)
        {}

        std::unique_ptr<ExitStrategy> clone() const override {
            return std::make_unique<StaticExitStrategy>(*this);
        }

        void update_stop_loss_price(BasePosition& position, const double&) override {
            if (position.is_long)
                this->stop_loss_price = position.entry_price - this->stop_loss_pip * position.market.pip_value;
            else
                this->stop_loss_price = position.entry_price + this->stop_loss_pip * position.market.pip_value;
        }

        void update_take_profit_price(BasePosition& position, const double&) override {
            if (position.is_long)
                this->take_profit_price = position.entry_price + this->take_profit_pip * position.market.pip_value;
            else
                this->take_profit_price = position.entry_price - this->take_profit_pip * position.market.pip_value;
        }
    };


class TrailingExitStrategy : public ExitStrategy {
    private:
        bool stop_loss_initialized = false;
        bool take_profit_initialized = false;
    public:
        TrailingExitStrategy(double stop_loss, double take_profit, const bool& save_price_data = false)
        : ExitStrategy(stop_loss, take_profit, save_price_data) {}

        std::unique_ptr<ExitStrategy> clone() const override {
            return std::make_unique<TrailingExitStrategy>(*this);
        }

        void update_stop_loss_price(BasePosition& position, const double& current_price) override {
            if (position.is_long) {
                double current_stop_loss_price = current_price - this->stop_loss_pip * position.market.pip_value;

                if (!this->stop_loss_initialized) {
                    this->stop_loss_price = current_stop_loss_price;
                    this->stop_loss_initialized = true;
                }

                if (current_stop_loss_price > this->stop_loss_price)
                    this->stop_loss_price = current_stop_loss_price;
            }
            else {
                double current_stop_loss_price = current_price + this->stop_loss_pip * position.market.pip_value;

                if (!this->stop_loss_initialized) {
                    this->stop_loss_price = current_stop_loss_price;
                    this->stop_loss_initialized = true;
                }

                if (current_stop_loss_price < this->stop_loss_price)
                    this->stop_loss_price = current_stop_loss_price;
            }
        }

        void update_take_profit_price(BasePosition& position, const double& current_price) override {
            if (position.is_long) {
                double current_take_profit_price = current_price + this->take_profit_pip * position.market.pip_value;

                if (!this->take_profit_initialized) {
                    this->take_profit_price = current_take_profit_price;
                    this->take_profit_initialized = true;
                }

                if (current_take_profit_price < this->take_profit_price)
                    this->take_profit_price = current_take_profit_price;
            }
            else {
                double current_take_profit_price = current_price - this->take_profit_pip * position.market.pip_value;

                if (!this->take_profit_initialized) {
                    this->take_profit_price = current_take_profit_price;
                    this->take_profit_initialized = true;
                }

                if (current_take_profit_price > this->take_profit_price)
                    this->take_profit_price = current_take_profit_price;
            }
        }
    };

class BreakEvenExitStrategy : public ExitStrategy {
    private:
        bool break_even_triggered = false;
        double break_even_trigger_pip;

    public:
        BreakEvenExitStrategy(double stop_loss, double take_profit, double break_even_trigger_pip, const bool& save_price_data = false)
        : ExitStrategy(stop_loss, take_profit, save_price_data),
            break_even_trigger_pip(break_even_trigger_pip) {}

        std::unique_ptr<ExitStrategy> clone() const override {
            return std::make_unique<BreakEvenExitStrategy>(*this);
        }

        void update_stop_loss_price(BasePosition& position, const double& current_price) override {
            if (!break_even_triggered) {
                // Normal SL until break-even level is hit
                if (position.is_long)
                    stop_loss_price = position.entry_price - stop_loss_pip * position.market.pip_value;
                else
                    stop_loss_price = position.entry_price + stop_loss_pip * position.market.pip_value;

                double distance_moved = std::abs(current_price - position.entry_price) / position.market.pip_value;
                if (distance_moved >= break_even_trigger_pip) {
                    stop_loss_price = position.entry_price;
                    break_even_triggered = true;
                }
            }
        }

        void update_take_profit_price(BasePosition& position, const double&) override {
            if (position.is_long)
                take_profit_price = position.entry_price + take_profit_pip * position.market.pip_value;
            else
                take_profit_price = position.entry_price - take_profit_pip * position.market.pip_value;
        }
    };


    using ExitStrategyPtr = std::shared_ptr<ExitStrategy>;