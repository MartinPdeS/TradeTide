#pragma once

#include <cmath>
#include <memory>
#include <vector>

#include "../market/market.h"
#include "../position/position.h"
#include "../state/state.h"

using TimePoint = std::chrono::system_clock::time_point;
using Duration = std::chrono::system_clock::duration;


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

        PositionPtr position;

        bool save_price_data = false; // Save the limit price for the position

        ExitStrategy(const double stop_loss_pip, const double take_profit_pip, const bool& save_price_data = false)
        : stop_loss_pip(stop_loss_pip), take_profit_pip(take_profit_pip), save_price_data(save_price_data) {}

        virtual std::unique_ptr<ExitStrategy> clone() const = 0;

        virtual void update_stop_loss_price() = 0;
        virtual void update_take_profit_price() = 0;

        void initialize_prices();

        void update_price();

};

class StaticExitStrategy : public ExitStrategy {
    public:
        StaticExitStrategy(double stop_loss_pip, double take_profit_pip, const bool& save_price_data = false)
        : ExitStrategy(stop_loss_pip, take_profit_pip, save_price_data)
        {}

        std::unique_ptr<ExitStrategy> clone() const override;

        void update_stop_loss_price() override;

        void update_take_profit_price() override;
    };


class TrailingExitStrategy : public ExitStrategy {
    public:
        TrailingExitStrategy(double stop_loss, double take_profit, const bool& save_price_data = false)
        : ExitStrategy(stop_loss, take_profit, save_price_data) {}

        std::unique_ptr<ExitStrategy> clone() const override;

        void update_stop_loss_price() override;

        void update_take_profit_price() override;

    };

class BreakEvenExitStrategy : public ExitStrategy {
    private:
        bool break_even_triggered = false;
        double break_even_trigger_pip;

    public:
        BreakEvenExitStrategy(double stop_loss, double take_profit, double break_even_trigger_pip, const bool& save_price_data = false)
        : ExitStrategy(stop_loss, take_profit, save_price_data),
            break_even_trigger_pip(break_even_trigger_pip) {}

        std::unique_ptr<ExitStrategy> clone() const override;

        void update_stop_loss_price() override;

        void update_take_profit_price() override;
    };


using ExitStrategyPtr = std::shared_ptr<ExitStrategy>;