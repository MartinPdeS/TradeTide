#pragma once

#include <memory>
#include <vector>
#include <limits>
#include <map>

#include "../position_collection/position_collection.h"
#include "../capital_management/capital_management.h"
#include "../state/state.h"
#include "../record/record.h"
#include "../metrics/metrics.h"



/**
 * @brief Simulates capital-constrained execution of trading signals.
 *
 * The Portfolio class selects and manages a subset of trading positions from
 * a PositionCollection, based on a capital management strategy. It supports
 * equity tracking, position activation, and various post-simulation analytics.
 */
class Portfolio {
public:
    /// Reference to the current state of the Portfolio plus interface to its history if enabled.
    State state;
    Record record;
    BaseCapitalManagement* capital_management;

    /// Reference to the source collection of all potential positions.
    PositionCollection& position_collection;

    std::vector<PositionPtr> selected_positions;  ///< Positions accepted for simulation
    std::vector<PositionPtr> active_positions;    ///< Currently open positions
    std::vector<PositionPtr> executed_positions;  ///< All positions ever opened

    /**
     * @brief Construct a Portfolio with a position source and capital strategy.
     *
     * @param position_collection A reference to the collection of all tradable signals.
     * @param capital_management  A capital management strategy that controls lot sizing.
     */
    Portfolio(PositionCollection& position_collection);

    /**
     * @brief Run the simulation using current strategy and portfolio constraints.
     */
    void simulate(BaseCapitalManagement& capital_management);

    /**
     * @brief Display final performance metrics in human-readable form.
     */
    void display() const;

    /**
     * @brief Get the Metrics object containing performance statistics.
     *
     * This method calculates and returns various performance metrics based on the
     * recorded history of the portfolio.
     *
     * @return Metrics object with calculated performance statistics.
     */
    Metrics get_metrics();

    /**
     * @return Final account equity after simulation.
     */
    [[nodiscard]] double final_equity() const;

    /**
     * @return Highest observed equity during the simulation.
     */
    [[nodiscard]] double peak_equity() const;

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
     * @brief Calculate the capital at risk based on all open positions.
     *
     * This is the sum of all positions' capital at risk.
     *
     * @return Total capital at risk.
     */
    [[nodiscard]] double calculate_capital_at_risk() const;

    /**
     * @brief Calculate the current equity of the portfolio.
     *
     * Equity is defined as the sum of initial capital and all open positions' values.
     *
     * @return Current equity value.
     */
    [[nodiscard]] double calculate_equity() const;


    /**
     * @brief Attempt to close all currently open positions based on their exit strategy.
     *
     * This method will iterate through all active positions and close them
     * if they meet the criteria defined by the exit strategy.
     */
    void try_close_positions();

    /**
     * @brief Attempt to open new positions based on the current capital management strategy.
     *
     * This method will iterate through the position collection and try to open
     * positions that meet the criteria defined by the capital management strategy.
     */
    void try_open_positions();

    /**
     * @brief Close all currently open positions at the current market price.
     *
     * This method will iterate through all active positions and close them,
     * updating the portfolio's equity and capital at risk accordingly.
     */
    void terminate_open_positions();

    /**
     * @brief Close a position at the current market price.
     *
     * This method will close the position at the current market price and update
     * the portfolio's equity and capital at risk accordingly.
     *
     * @param position Reference to the PositionPtr that will be closed.
     * @param position_idx Index of the position in the active positions vector.
     */
    void close_position(PositionPtr& position, const size_t &position_idx);

    /**
     * @brief Open a new position based on the provided capital management strategy.
     *
     * This method will attempt to open a position using the specified capital management
     * strategy, which determines lot sizing and risk management.
     *
     * @param position Reference to the PositionPtr that will be opened.
     */
    void open_position(PositionPtr& position);
};
