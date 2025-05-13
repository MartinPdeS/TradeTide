#pragma once

#include <string>
#include <chrono>
#include <ctime>
#include "../market/market.h"


using TimePoint   = std::chrono::system_clock::time_point;

class PipManager;  // forward declaration


class BasePosition {
    public:
        const Market& market;
        std::unique_ptr<PipManager> risk_managment;
        double entry_price;        // Price at which the position is opened
        double exit_price;         // Price at which the position is closed
        double lot_size;           // Size of the position in lots
        bool is_closed;            // Status of the position
        size_t start_idx;

        TimePoint start_date; // Time when position was opened
        TimePoint close_date; // Time when position was closed


        virtual ~BasePosition() = default;

        BasePosition(const Market& market, std::unique_ptr<PipManager> risk_managment, const size_t start_idx)
        :
            market(market),
            risk_managment(std::move(risk_managment)),
            entry_price(0.0),
            exit_price(0.0),
            is_closed(false),
            start_idx(start_idx) {}

        // Close the position for a certain market_price
        virtual void close(const size_t time_idx) = 0;
        void close_at_stop_loss(const size_t time_idx);
        void close_at_take_profit(const size_t time_idx);

        // Calculate profit or loss
        virtual double calculate_profite_and_loss() const = 0;

        // Display Position Info
        virtual void display() const = 0;

        // Check if stop-loss or take-profit is hit
        virtual void check_exit_conditions(const size_t time_idx) = 0;


        const std::vector<double>& stop_loss_prices() const;
        const std::vector<double>& take_profit_prices() const;
        const std::vector<TimePoint>& dates() const;
};

class Long : public BasePosition {
    public:
        Long(const Market& market, std::unique_ptr<PipManager> risk_managment, const size_t start_idx)
        : BasePosition(market, std::move(risk_managment), start_idx){
            this->start_date = this->market.dates[start_idx];
            this->open(start_idx);
        }

        // Open the position for a certain market_price
        void open(const size_t time_idx);

        // Close the position for a certain market_price
        void close(const size_t time_idx) override;

        double calculate_profite_and_loss() const override;

        void display() const override;

        void check_exit_conditions(const size_t time_idx) override;
    };


class Short : public BasePosition {
    public:
        Short(const Market& market, std::unique_ptr<PipManager> risk_managment, const size_t start_idx)
        : BasePosition(market, std::move(risk_managment), start_idx){
            this->start_date = this->market.dates[start_idx];
            this->open(start_idx);
        }

        // Open the position for a certain market_price
        void open(const size_t time_idx);

        // Close the position for a certain market_price
        void close(const size_t time_idx) override;

        double calculate_profite_and_loss() const override;

        void display() const override;

        void check_exit_conditions(const size_t time_idx) override;
    };
