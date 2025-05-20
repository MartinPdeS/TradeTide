#pragma once

#include <string>
#include <memory>
#include <chrono>
#include <vector>
#include "../market/market.h"

using TimePoint = std::chrono::system_clock::time_point;

class ExitStrategy;  // Forward declaration

/**
 * @brief Abstract base class representing a trading position.
 *
 * Stores shared metadata for both Long and Short positions, including entry/exit prices,
 * timestamps, and linkage to an ExitStrategy. Concrete position logic (e.g., profit direction)
 * is defined in derived classes.
 */
class BasePosition {
public:
    const Market& market;  ///< Reference to market data
    std::unique_ptr<ExitStrategy> exit_strategy; ///< Exit strategy used for this position

    double entry_price = 0.0;     ///< Entry price of the position
    double exit_price = 0.0;      ///< Exit price when position is closed
    double lot_size = 1.0;        ///< Trade size in lots

    TimePoint start_date;         ///< Timestamp when position is opened
    TimePoint close_date;         ///< Timestamp when position is closed
    size_t open_idx = 0;          ///< Index in market data when position opens
    size_t close_idx = 0;

    bool is_long = true;          ///< True if this is a long position
    bool is_closed = false;       ///< True if this position has been closed

    virtual ~BasePosition() = default;

    /**
     * @brief Constructs a new BasePosition.
     *
     * @param market Reference to market data
     * @param exit_strategy Exit strategy to apply
     * @param entry_price Price at which the position is opened
     * @param start_date Date/time of opening
     * @param start_idx Index in the market series where position starts
     * @param is_long True if long, false if short
     */
    BasePosition(const Market& market,
                 std::unique_ptr<ExitStrategy> exit_strategy,
                 double entry_price,
                 TimePoint start_date,
                 size_t open_idx,
                 bool is_long)
        : market(market),
          exit_strategy(std::move(exit_strategy)),
          entry_price(entry_price),
          start_date(start_date),
          open_idx(open_idx),
          is_long(is_long),
          is_closed(false)
    {}

    /**
     * @brief Runs SL/TP logic and attempts to close the position accordingly.
     */
    virtual void propagate() = 0;

    /**
     * @brief Closes the position at the stop-loss price.
     */
    void close_at_stop_loss(size_t time_idx);

    /**
     * @brief Closes the position at the take-profit price.
     */
    void close_at_take_profit(size_t time_idx);

    /**
     * @brief Calculates profit or loss of the position.
     * @return PnL as a double (positive = profit, negative = loss)
     */
    [[nodiscard]] virtual double calculate_profit_and_loss() const = 0;
    [[nodiscard]] virtual double calculate_profit_and_loss_time(const size_t&) const = 0;

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

    /**
     * @brief Returns timestamps at which SL/TP values were updated.
     */
    const std::vector<TimePoint>& strategy_dates() const;

    /**
     * @brief Helper method to close position at a specific price and time index.
     */
    void close(const double& price, const size_t& time_idx) {
        this->exit_price = price;
        this->close_date = this->market.dates[time_idx];
        this->close_idx = time_idx;
        this->is_closed = true;
    }

    /**
     * @brief Closes the position at the market price at the given index.
     */
    virtual void close(const size_t time_idx) = 0;

    bool is_open(const TimePoint& date) {
        if (date > this->start_date && date < this->close_date)
            return true;
        return false;
    }
};

/**
 * @brief Represents a long position (profits if market rises).
 */
class Long : public BasePosition {
public:
    Long(const Market& market,
         std::unique_ptr<ExitStrategy> exit_strategy,
         double entry_price,
         TimePoint start_date,
         size_t start_idx)
        : BasePosition(market, std::move(exit_strategy), entry_price, start_date, start_idx, true)
    {}

    void propagate() override;
    [[nodiscard]] double calculate_profit_and_loss() const override;
    [[nodiscard]] double calculate_profit_and_loss_time(const size_t& time_idx) const override;
    void display() const override;

    void close(const size_t time_idx) override {
        this->exit_price = (*this->market.bid.price)[time_idx];
        this->close_date = this->market.dates[time_idx];
        this->is_closed = true;
    }
};

/**
 * @brief Represents a short position (profits if market falls).
 */
class Short : public BasePosition {
public:
    Short(const Market& market,
          std::unique_ptr<ExitStrategy> exit_strategy,
          double entry_price,
          TimePoint start_date,
          size_t start_idx)
        : BasePosition(market, std::move(exit_strategy), entry_price, start_date, start_idx, false)
    {}

    void propagate() override;
    [[nodiscard]] double calculate_profit_and_loss() const override;
    [[nodiscard]] double calculate_profit_and_loss_time(const size_t&) const override;
    void display() const override;

    void close(const size_t time_idx) override {
        this->exit_price = (*this->market.ask.price)[time_idx];
        this->close_date = this->market.dates[time_idx];
        this->is_closed = true;
    }
};

/**
 * @brief Shared pointer type for polymorphic position management.
 */
using PositionPtr = std::shared_ptr<BasePosition>;
