#pragma once

#include <iostream>
#include <chrono>
#include <vector>
#include "../market/market.h"
#include "../state/state.h"
#include "../exit_strategy/exit_strategy.h"

using TimePoint = std::chrono::system_clock::time_point;

/**
 * @brief Abstract base class representing a trading position.
 *
 * Stores shared metadata for both Long and Short positions, including entry/exit prices,
 * timestamps, and linkage to an ExitStrategy. Concrete position logic (e.g., profit direction)
 * is defined in derived classes.
 */
class BasePosition {
public:
    std::unique_ptr<ExitStrategy> exit_strategy; ///< Exit strategy used for this position

    double entry_price = 0.0;      ///< Entry price of the position
    double exit_price = 0.0;       ///< Exit price when position is closed
    double lot_size = 1.0;         ///< Trade size in lots

    TimePoint start_date;          ///< Timestamp when position is opened
    TimePoint close_date;          ///< Timestamp when position is closed
    size_t start_idx = 0;          ///< Index in market data when position opens
    size_t close_idx = 0;          ///< Index in market data when position closes

    bool is_long = true;           ///< True if this is a long position
    bool is_closed = false;        ///< True if this position has been closed
    bool is_terminated = false;

    State state;                   ///< Current state of the position, including market data

    virtual ~BasePosition() = default;

    /**
     * @brief Constructs a new BasePosition.
     *
     * @param exit_strategy Exit strategy to apply
     * @param entry_price Price at which the position is opened
     * @param start_date Date/time of opening
     * @param start_idx Index in the market series where position starts
     * @param is_long True if long, false if short
     */
    BasePosition(const ExitStrategy &exit_strategy, size_t start_idx, bool is_long);

    /**
     * @brief Runs SL/TP logic and attempts to close the position accordingly.
     */
    virtual void propagate() = 0;

    /**
     * @brief Calculates profit or loss of the position.
     * @return PnL as a double (positive = profit, negative = loss)
     */
    [[nodiscard]] virtual double get_price_difference() const = 0;

    /**
     * @brief Prints position summary to console.
     */
    virtual void display() const = 0;

    /**
     * @brief Returns stop-loss price history from the ExitStrategy.
     */
    const std::vector<double>& strategy_stop_loss_prices() const;

    /**
     * @brief Returns take-profit price history from the ExitStrategy.
     */
    const std::vector<double>& strategy_take_profit_prices() const;

    double get_capital_at_risk() const;

    /**
     * @brief Returns timestamps at which SL/TP values were updated.
     */
    const std::vector<TimePoint>& strategy_dates() const;

    /**
     * @brief Terminates the position at the given exit price and time index.
     *
     * This is called when the position is closed either by hitting SL/TP or manually.
     * @param exit_price Price at which the position is closed.
     * @param time_idx Index in the market data when the position is closed.
     */
    void terminate(const double exit_price, const size_t time_idx);


    /**
     * @brief Closes the position at the market price at the given index.
     */
    virtual void set_close_condition(const size_t time_idx) = 0;

    /**
     * @brief Checks if the position is open at a specific date.
     *
     * This is used to determine if the position is active during a given time point.
     * @param date TimePoint to check.
     * @return True if the position is open at that date, false otherwise.
     */
    [[nodiscard]] bool is_open_at(const TimePoint& date) const {
        if (date > this->start_date && date < this->close_date)
            return true;
        return false;
    }

    /**
     * @brief Returns the closing value of the position at a specific time index.
     *
     * This is used to calculate the value of the position at a given time point.
     * @param time_idx Index in the market data to get the closing value for.
     * @return Closing value as a double.
     */
    virtual double get_closing_value_at(const size_t time_idx) const = 0;

    /**
     * @brief Returns the closing price of the position.
     *
     * This is used to get the final price at which the position was closed.
     * @return Closing price as a double.
     */
    virtual double get_closing_price() = 0;

    /**
     * @brief Initializes the state of the position.
     *
     * @param market Reference to the Market object containing market data.
     * @param time_idx Index in the market data to initialize the state with.
     */
    void initialize_state(const Market& market, const size_t time_idx);

};

/**
 * @brief Represents a long position (profits if market rises).
 */
class Long : public BasePosition {
public:
    Long(const ExitStrategy &exit_strategy, const size_t time_idx, const Market &market);

    void propagate() override;

    void display() const override;

    void set_close_condition(const size_t time_idx) override;

    double get_closing_value_at(const size_t time_idx) const override;

    [[nodiscard]] double get_price_difference() const override;

    double get_closing_price() override  {return this->state.bid.close;};;
};

/**
 * @brief Represents a short position (profits if market falls).
 */
class Short : public BasePosition {
public:
    Short(const ExitStrategy &exit_strategy, const size_t time_idx, const Market &market);

    void propagate() override;

    void display() const override;

    void set_close_condition(const size_t time_idx) override;

    double get_closing_value_at(const size_t time_idx) const override;

    [[nodiscard]] double get_price_difference() const override;

    double get_closing_price() override {return this->state.ask.close;};
};

/**
 * @brief Shared pointer type for polymorphic position management.
 */
using PositionPtr = std::shared_ptr<BasePosition>;
