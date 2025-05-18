#pragma once

#include <string>
#include <chrono>
#include <ctime>
#include "../market/market.h"


using TimePoint   = std::chrono::system_clock::time_point;

class ExitStrategy;  // forward declaration

/**
 * Base class for all trading positions.
 * Supports shared logic for open/close time, pricing, and exit strategy.
 */
class BasePosition {
    public:
        const Market& market;
        std::unique_ptr<ExitStrategy> exit_strategy;

        double entry_price;        // Price at which the position is opened
        double exit_price;         // Price at which the position is closed
        double lot_size;           // Size of the position in lots

        TimePoint start_date; // Time when position was opened
        TimePoint close_date; // Time when position was closed
        size_t start_idx;

        bool is_long;
        bool is_closed;            // Status of the position


        virtual ~BasePosition() = default;

        BasePosition(const Market& market, std::unique_ptr<ExitStrategy> exit_strategy, const double entry_price, const TimePoint start_date, const size_t start_idx, const bool is_long)
        : market(market), exit_strategy(std::move(exit_strategy)), entry_price(entry_price), start_date(start_date), start_idx(start_idx), is_long(is_long), is_closed(false)
        {}

        // Close the position for a certain market_price
        virtual void propagate() = 0;


        void close_at_stop_loss(const size_t time_idx);
        void close_at_take_profit(const size_t time_idx);

        // Calculate profit or loss
        [[nodiscard]] virtual double calculate_profite_and_loss() const = 0;

        // Display Position Info
        virtual void display() const = 0;

        const std::vector<double>& strategy_stop_loss_prices() const;
        const std::vector<double>& strategy_take_profit_prices() const;
        const std::vector<TimePoint>& strategy_dates() const;

        void close(const double& price, const size_t time_idx) {
            this->exit_price = price;
            close_date = market.dates[time_idx];
            is_closed = true;
        }

        virtual void close(const size_t time_idx) = 0;
};

/// Long trading position (profit if market goes up)
class Long : public BasePosition {
    public:
        Long(const Market& market, std::unique_ptr<ExitStrategy> exit_strategy, const double entry_price, const TimePoint start_date, const size_t start_idx)
        : BasePosition(market, std::move(exit_strategy), entry_price, start_date, start_idx, true)
        {}

        // Close the position for a certain market_price
        void propagate() override;

        double calculate_profite_and_loss() const override;

        void display() const override;

        void close(const size_t time_idx) override {
            this->exit_price = (*this->market.bid.price)[time_idx];
            close_date = market.dates[time_idx];
            is_closed = true;
        }
    };


/// Short trading position (profit if market goes down)
class Short : public BasePosition {
    public:
        Short(const Market& market, std::unique_ptr<ExitStrategy> exit_strategy, const double entry_price, const TimePoint start_date, const size_t start_idx)
        : BasePosition(market, std::move(exit_strategy), entry_price, start_date, start_idx, false)
        {}

        // Close the position for a certain market_price
        void propagate() override;

        double calculate_profite_and_loss() const override;

        void display() const override;

        void close(const size_t time_idx) override {
            this->exit_price = (*this->market.ask.price)[time_idx];
            close_date = market.dates[time_idx];
            is_closed = true;
        }
    };
