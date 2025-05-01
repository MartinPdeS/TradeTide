#pragma once

#include <string>
#include <chrono>
#include <ctime>
#include "../market/market.h"


class RiskManagment;  // forward declaration


class Position {
public:
    bool is_long;              // true for long, false for short
    double entry_price;        // Price at which the position is opened
    double exit_price;         // Price at which the position is closed
    double lot_size;           // Size of the position in lots
    double pip_price;          // Pip value for the position
    double stop_loss;          // Stop-loss price level
    double take_profit;        // Take-profit price level
    bool is_closed;            // Status of the position
    std::chrono::system_clock::time_point start_date; // Time when position was opened
    std::chrono::system_clock::time_point close_date; // Time when position was closed

public:
    // Constructor
    Position() = default;

    Position(bool long_position, double price, double lots, double pip_val, double stop_loss, double take_profit)
        : is_long(long_position), entry_price(price), exit_price(0.0), lot_size(lots), pip_price(pip_val),
          stop_loss(stop_loss), take_profit(take_profit), is_closed(false) {}

    // Open Position
    void open(double price);

    // Close the position and calculate profit or loss
    void close(double market_price);

    // Check if stop-loss or take-profit is hit
    bool check_exit_conditions(const double high_price, const double low_price);

    // Calculate profit or loss
    double calculate_pnl() const;

    void display() const;

};



class BasePosition {
    public:
        const Market& market;
        const RiskManagment& risk_managment;
        double entry_price;        // Price at which the position is opened
        double exit_price;         // Price at which the position is closed
        double lot_size;           // Size of the position in lots
        double pip_price;          // Pip value for the position
        bool is_closed;            // Status of the position
        size_t start_idx;

        std::chrono::system_clock::time_point start_date; // Time when position was opened
        std::chrono::system_clock::time_point close_date; // Time when position was closed

        virtual ~BasePosition() = default;

        BasePosition(const Market& market, const RiskManagment& risk_managment, const double entry_price, const double lot_size, const double pip_val, const size_t start_idx)
        :
            market(market),
            risk_managment(risk_managment),
            entry_price(entry_price),
            exit_price(0.0),
            lot_size(lot_size),
            pip_price(pip_val),
            is_closed(false),
            start_idx(start_idx) {
                start_date = this->market.dates[start_idx];
            }

        // Open the position for a certain market_price
        void open(const double price);

        // Close the position for a certain market_price
        void close(const double market_price);

        // Calculate profit or loss
        virtual double calculate_pnl() const = 0;

        // Display Position Info
        virtual void display() const = 0;

        // Check if stop-loss or take-profit is hit
        virtual void check_exit_conditions(const size_t time_idx) = 0;
};

class Long : public BasePosition {
    public:
        using BasePosition::BasePosition;

        double calculate_pnl()  const override;

        void display() const override;

        void check_exit_conditions(const size_t time_idx) override;
    };


class Short : public BasePosition {
    public:
        using BasePosition::BasePosition;

        double calculate_pnl() const override;

        void display() const override;

        void check_exit_conditions(const size_t time_idx) override;
    };
