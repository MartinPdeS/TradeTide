#pragma once

#include <cmath>
#include <memory>
#include <vector>

#include "../market/market.h"
#include "../state/state.h"

using TimePoint = std::chrono::system_clock::time_point;
using Duration = std::chrono::system_clock::duration;

class BasePosition; // Forward declaration of BasePosition


class ExitStrategy {
    protected:
        /**
         * @brief Updates the stop-loss price based on the current market conditions.
         *
         * This method is pure virtual and must be implemented by derived classes.
         */
        virtual void update_stop_loss_price() = 0;

        /**
         * @brief Updates the take-profit price based on the current market conditions.
         *
         * This method is pure virtual and must be implemented by derived classes.
         */
        virtual void update_take_profit_price() = 0;

    public:
        virtual ~ExitStrategy() {};

        double stop_loss_pip;    // Distance (in pips) for stop-loss from the entry price
        double take_profit_pip;  // Distance (in pips) for take-profit from the entry price

        double stop_loss_price = 0; // Current stop-loss price
        double take_profit_price = 0; // Current take-profit price

        std::vector<double> stop_loss_prices;   // Historical stop-loss prices
        std::vector<double> take_profit_prices;  // Historical take-profit prices
        std::vector<TimePoint> dates;            // Timestamps for each price update

        BasePosition *position; // Pointer to the position this exit strategy is applied to

        bool save_price_data = false; // Save the limit price for the position

        ExitStrategy(const double stop_loss_pip, const double take_profit_pip, const bool& save_price_data = false)
        : stop_loss_pip(stop_loss_pip), take_profit_pip(take_profit_pip), save_price_data(save_price_data) {}

        /**
         * @brief Clones the exit strategy.
         * @return A unique pointer to the cloned exit strategy.
         */
        virtual std::unique_ptr<ExitStrategy> clone() const = 0;

        /**
         * @brief Initializes the stop-loss and take-profit prices based on the entry price.
         */
        void initialize_prices();

        /**
         * @brief Updates the stop-loss and take-profit prices based on the current market state.
         *
         * This method is called to adjust the exit strategy prices dynamically during position management.
         */
        void update_price();

};

class StaticExitStrategy : public ExitStrategy {
    private:
        /**
         * @brief Updates the stop-loss price. This is a static strategy, so it does not change.
         */
        void update_stop_loss_price() override;

        /**
         * @brief Updates the take-profit price. This is a static strategy, so it does not change.
         */
        void update_take_profit_price() override;

    public:
        StaticExitStrategy(double stop_loss_pip, double take_profit_pip, const bool& save_price_data = false)
        : ExitStrategy(stop_loss_pip, take_profit_pip, save_price_data)
        {}

        /**
         * @brief Clones the static exit strategy.
         * @return A unique pointer to the cloned static exit strategy.
         */
        std::unique_ptr<ExitStrategy> clone() const override;
    };


class TrailingExitStrategy : public ExitStrategy {
    private:
        /**
         * @brief Updates the stop-loss price based on the trailing logic.
         *
         * This method adjusts the stop-loss price to trail the market price.
         */
        void update_stop_loss_price() override;

        /**
         * @brief Updates the take-profit price based on the trailing logic.
         *
         * This method adjusts the take-profit price to trail the market price.
         */
        void update_take_profit_price() override;

    public:
        TrailingExitStrategy(double stop_loss, double take_profit, const bool& save_price_data = false)
        : ExitStrategy(stop_loss, take_profit, save_price_data) {}

        /**
         * @brief Clones the trailing exit strategy.
         * @return A unique pointer to the cloned trailing exit strategy.
         */
        std::unique_ptr<ExitStrategy> clone() const override;
    };

class BreakEvenExitStrategy : public ExitStrategy {
    protected:
        /**
         * @brief Updates the stop-loss price to break-even if the trigger condition is met.
         *
         * This method checks if the break-even condition is satisfied and adjusts the stop-loss price accordingly.
         */
        void update_stop_loss_price() override;

        /**
         * @brief Updates the take-profit price. This is a static strategy, so it does not change.
         */
        void update_take_profit_price() override;

    private:
        bool break_even_triggered = false;
        double break_even_trigger_pip;

    public:
        BreakEvenExitStrategy(double stop_loss, double take_profit, double break_even_trigger_pip, const bool& save_price_data = false)
        : ExitStrategy(stop_loss, take_profit, save_price_data),
            break_even_trigger_pip(break_even_trigger_pip) {}

        /**
         * @brief Clones the break-even exit strategy.
         * @return A unique pointer to the cloned break-even exit strategy.
         */
        std::unique_ptr<ExitStrategy> clone() const override;
    };


using ExitStrategyPtr = std::shared_ptr<ExitStrategy>;
