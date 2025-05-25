#pragma once

#include <vector>
#include <memory>
#include <string>
#include <algorithm>
#include "../market/market.h"
#include "../signal/signal.h"
#include "../position/position.h"
#include "../exit_strategy/exit_strategy.h"

using TimePoint = std::chrono::system_clock::time_point;

/**
 * @brief Manages a collection of trading positions over a given market and signal.
 *
 * This class handles the creation, management, and evaluation of multiple positions
 * (long or short) based on a provided signal and market data. It supports export,
 * filtering, and access operations for high-level analysis.
 */
class PositionCollection {
private:
    /**
     * @brief Generic helper to extract a vector of any value from each position.
     *
     * @tparam dtype      Type of value to extract.
     * @tparam function   Function that extracts dtype from a PositionPtr.
     * @param accessor    Lambda or function pointer.
     * @return std::vector<dtype> Resulting vector of extracted values.
     */
    template <typename dtype, typename function>
    std::vector<dtype> extract_vector(function accessor) {
        std::vector<dtype> array;
        array.reserve(this->positions.size());

        for (const PositionPtr& position : this->positions)
            array.push_back(accessor(position));

        return array;
    }

public:
    const Market market;                             ///< Market data reference
    const ExitStrategyPtr exit_strategy_ptr;         ///< Shared exit strategy template
    const std::vector<double> trade_signal;               ///< Signal stream for entry logic
    std::vector<PositionPtr> positions;              ///< All tracked positions
    size_t number_of_trade = 0;                      ///< Number of trades detected from signal
    bool save_price_data = false;                    ///< Whether to store SL/TP traces

    /**
     * @brief Default constructor.
     */
    PositionCollection() = default;

    /**
     * @brief Constructs a new PositionCollection.
     *
     * @param market Reference to market series.
     * @param exit_strategy_ptr Shared pointer to exit strategy template.
     * @param signal Trade signal series.
     * @param save_price_data Enables SL/TP tracing per position.
     */
    PositionCollection(
        const Market& market,
        const ExitStrategyPtr& exit_strategy_ptr,
        // const Signal& signal,
        const std::vector<double>& trade_signal,
        const bool save_price_data = false)
        : market(market),
          exit_strategy_ptr(exit_strategy_ptr),
          trade_signal(trade_signal),
          save_price_data(save_price_data)
    {
        this->number_of_trade = std::count_if(
            this->trade_signal.begin(),
            this->trade_signal.end(),
            [](int x) { return x != 0; }
        );

        this->positions.reserve(this->number_of_trade);
    }

    /**
     * @brief Initializes positions according to the provided signal.
     */
    void open_positions();

    /**
     * @brief Propagates each position to closure using market data and exit strategy.
     */
    void propagate_positions();

    /**
     * @brief Force-closes any remaining open positions at final market price.
     */
    void terminate_open_positions();

    /**
     * @brief Displays summary information for all positions.
     */
    void display() const;

    /**
     * @brief Get position by index (Python-style).
     * @throws std::out_of_range
     * @param idx Index of position.
     * @return Raw pointer to position.
     */
    BasePosition* __getitem__(const size_t idx) const;
    /**
     * @brief Returns the number of positions.
     */
    size_t __len__() const { return this->positions.size(); }

    /**
     * @brief Returns the number of stored positions.
     */
    [[nodiscard]] size_t size() const { return this->positions.size(); }

    /**
     * @brief Export the entire position set to a CSV file.
     * @param filepath Path to output file.
     */
    void to_csv(const std::string& filepath) const;

    /**
     * @brief Index access operator.
     */
    const PositionPtr& operator[](size_t i) const {
        return this->positions[i];
    }

    /**
     * @brief Returns vector of open dates.
     */
    [[nodiscard]] std::vector<TimePoint> get_start_dates() {
        return this->extract_vector<TimePoint>(
            [](const PositionPtr& p) { return p->start_date; });
    }

    /**
     * @brief Returns vector of close dates.
     */
    [[nodiscard]] std::vector<TimePoint> get_close_dates() {
        return this->extract_vector<TimePoint>(
            [](const PositionPtr& p) { return p->close_date; });
    }

    /**
     * @brief Returns vector of entry prices.
     */
    [[nodiscard]] std::vector<double> get_entry_prices() {
        return this->extract_vector<double>(
            [](const PositionPtr& p) { return p->entry_price; });
    }

    /**
     * @brief Returns vector of exit prices.
     */
    [[nodiscard]] std::vector<double> get_exit_prices() {
        return this->extract_vector<double>(
            [](const PositionPtr& p) { return p->exit_price; });
    }

    /**
     * @brief Access the underlying market reference.
     */
    const Market& get_market() const {
        return this->market;
    }

    /**
     * @brief Get up to `count` long positions.
     * @param count Max number to return. Default: all.
     */
    [[nodiscard]] std::vector<Long*> get_long_positions(size_t count) const;

    /**
     * @brief Get up to `count` short positions.
     * @param count Max number to return. Default: all.
     */
    [[nodiscard]] std::vector<Short*> get_short_positions(size_t count) const;

    /**
     * @brief Get up to `count` of all positions (both long and short).
     * @param count Max number to return. Default: all.
     */
    [[nodiscard]] std::vector<BasePosition*> get_all_positions(size_t count) const;
};
