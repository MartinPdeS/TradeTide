#pragma once

#include <memory>
#include <vector>
#include <limits>

#include "../position_collection/position_collection.h"
#include "../capital_management/capital_management.h"

/**
 * @brief Simulates capital-constrained execution of trading signals.
 *
 * The Portfolio class selects and manages a subset of trading positions from
 * a PositionCollection, based on a capital management strategy. It supports
 * equity tracking, position activation, and various post-simulation analytics.
 */
class Portfolio {
private:
    TimePoint current_time;

public:
    /// Reference to the source collection of all potential positions.
    PositionCollection& position_collection;

    /// Reference to the capital management strategy used for lot sizing.
    BaseCapitalManagement& capital_management;

    /**
     * @brief Construct a Portfolio with a position source and capital strategy.
     *
     * @param position_collection A reference to the collection of all tradable signals.
     * @param capital_management  A capital management strategy that controls lot sizing.
     */
    Portfolio(PositionCollection& position_collection, BaseCapitalManagement& capital_management)
        : position_collection(position_collection), capital_management(capital_management) {}

    /**
     * @brief Run the simulation using current strategy and portfolio constraints.
     */
    void simulate();

    /**
     * @brief Display final performance metrics in human-readable form.
     */
    void display() const;

    /**
     * @return Final account equity after simulation.
     */
    [[nodiscard]] double final_equity() const;

    /**
     * @return Highest observed equity during the simulation.
     */
    [[nodiscard]] double peak_equity() const;

    /**
     * @return Full equity curve over time.
     */
    [[nodiscard]] std::vector<double> equity_curve() const;

    /**
     * @return Market time series from the underlying PositionCollection.
     */
    [[nodiscard]] const std::vector<TimePoint>& get_market_dates() const;

    /**
     * @return A reference to the associated Market object.
     */
    [[nodiscard]] const Market& get_market() { return this->position_collection.market; }

    /**
     * @brief Get up to `count` of all positions that were selected by the Portfolio.
     * @param count The maximum number of positions to return (default: all).
     * @return Vector of BasePosition* to selected trades.
     */
    [[nodiscard]] std::vector<BasePosition*> get_positions(size_t count = std::numeric_limits<size_t>::max()) const;

    /**
     * @brief Compute a time-aligned vector of open position counts.
     *
     * This corresponds to the number of positions active at each time step.
     */
    void compute_open_position_count_over_time();

    /**
     * @brief Compute the equity curve based on realized profits and losses.
     */
    void compute_equity_over_time();

    /// Vector of realized equity values at each time step.
    std::vector<double> equity_history;

    /// Vector of open position counts at each time step.
    std::vector<size_t> open_position_count;


    [[nodiscard]] double calculate_total_return() const;
    [[nodiscard]] double calculate_annualized_return(double total_return) const;
    [[nodiscard]] std::chrono::duration<double> calculate_duration() const;
    [[nodiscard]] double calculate_max_drawdown() const;
    [[nodiscard]] double calculate_sharpe_ratio(double risk_free_rate = 0.0) const;
    [[nodiscard]] double calculate_sortino_ratio(double risk_free_rate = 0.0) const;
    [[nodiscard]] double calculate_win_loss_ratio() const;
    [[nodiscard]] double calculate_equity() const;
    [[nodiscard]] double calculate_volatility() const;


private:
    /// Positions selected from the pool that passed capital constraints.
    std::vector<PositionPtr> selected_positions;

    /// Positions currently active (open) during simulation.
    std::vector<PositionPtr> active_positions;

    /// All positions that were executed (closed or open).
    std::vector<PositionPtr> executed_positions;

    /// Reset simulation state prior to running.
    void reset_state();
};
