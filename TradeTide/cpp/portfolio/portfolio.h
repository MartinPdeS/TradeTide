#pragma once

#include <memory>
#include <vector>
#include <limits>

#include "../position_collection/position_collection.h"
#include "../capital_management/capital_management.h"
#include "../state/state.h"
#include "../record/record.h"


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
    Portfolio(PositionCollection& position_collection, bool record_enabled)
        : position_collection(position_collection)
        {
            this->record.state = &this->state;

            this->record.start_record(this->position_collection.market.dates.size());

        }

    [[nodiscard]] const std::vector<size_t>& get_history_position_count() {return this->record.concurrent_positions;}

    [[nodiscard]] const std::vector<double>& get_history_equity() {return this->record.equity;}
    [[nodiscard]] const std::vector<double>& get_history_capital_at_risk() {return this->record.capital_at_risk;}
    /**
     * @brief Run the simulation using current strategy and portfolio constraints.
     */
    void simulate(BaseCapitalManagement& capital_management);

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
     * @brief Compute total return over the entire simulation period.
     *
     * @return Total return as a fraction (e.g., 0.12 for +12% gain).
     */
    [[nodiscard]] double calculate_total_return() const;

    /**
     * @brief Calculate the annualized (compounded) return from total return.
     *
     * @param total_return The total return (from calculate_total_return).
     * @return Annualized return as a fraction (e.g., 0.08 for +8% per year).
     */
    [[nodiscard]] double calculate_annualized_return(double total_return) const;

    /**
     * @brief Compute the total duration of the simulation.
     *
     * @return Duration as a std::chrono::duration in seconds.
     */
    [[nodiscard]] std::chrono::duration<double> calculate_duration() const;

    /**
     * @brief Compute the maximum drawdown during the simulation.
     *
     * Max drawdown is the largest peak-to-trough equity drop as a fraction of the peak.
     *
     * @return Maximum drawdown (e.g., 0.25 for -25%).
     */
    [[nodiscard]] double calculate_max_drawdown() const;

    /**
     * @brief Compute the Sharpe ratio (risk-adjusted return).
     *
     * @param risk_free_rate Optional risk-free rate (default = 0).
     * @return Sharpe ratio (mean excess return divided by standard deviation of returns).
     */
    [[nodiscard]] double calculate_sharpe_ratio(double risk_free_rate = 0.0) const;

    /**
     * @brief Compute the Sortino ratio (risk-adjusted return using downside risk).
     *
     * @param risk_free_rate Optional risk-free rate (default = 0).
     * @return Sortino ratio (mean excess return divided by downside deviation).
     */
    [[nodiscard]] double calculate_sortino_ratio(double risk_free_rate = 0.0) const;

    /**
     * @brief Calculate the win/loss ratio of executed trades.
     *
     * @return Ratio of winning trades to losing trades (e.g., 1.5 for 60% win, 40% loss).
     */
    [[nodiscard]] double calculate_win_loss_ratio() const;

    /**
     * @brief Return the final portfolio equity.
     *
     * Equivalent to capital at the end of the simulation.
     *
     * @return Final equity.
     */
    [[nodiscard]] double calculate_equity() const;

    /**
     * @brief Compute the portfolio's volatility.
     *
     * Volatility is defined as the standard deviation of periodic returns.
     *
     * @return Volatility (e.g., 0.05 for 5%).
     */
    [[nodiscard]] double calculate_volatility() const;

    /**
     * @brief Calculate the capital at risk based on all open positions.
     *
     * This is the sum of all positions' capital at risk.
     *
     * @return Total capital at risk.
     */
    [[nodiscard]] double calculate_capital_at_risk() const;

    /** @brief Attempt to close positions based on current market conditions. */
    void try_close_positions(BaseCapitalManagement& capital_management);

    /** @brief Attempt to open new positions based on current market conditions. */
    void try_open_positions(BaseCapitalManagement& capital_management);

    /** @brief Terminate all open positions. */
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
     * @param capital_management The capital management strategy to use for opening the position.
     */
    void open_position(PositionPtr& position, const BaseCapitalManagement &capital_management);
};
