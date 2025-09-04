/**
 * @file metrics.h
 * @brief Performance metrics calculation for trading portfolios
 *
 * This file contains the Metrics class which provides comprehensive performance
 * analysis capabilities for trading simulations, including risk metrics, return
 * calculations, and various financial ratios.
 */

#pragma once

#include <vector>
#include <chrono>
#include <algorithm>

#include "../record/record.h"
// #include "../portfolio/portfolio.h"

/// Type alias for system clock duration representation
using Duration = std::chrono::system_clock::duration;
/// Type alias for system clock time point representation
using TimePoint = std::chrono::system_clock::time_point;


/**
 * @class Metrics
 * @brief Comprehensive performance metrics calculator for trading portfolios
 *
 * The Metrics class provides a complete suite of performance analysis tools for
 * evaluating trading strategies and portfolio performance. It calculates standard
 * financial metrics including returns, risk measures, and ratios commonly used
 * in quantitative finance and algorithmic trading.
 *
 * Key features:
 * - Risk-adjusted returns (Sharpe ratio, Sortino ratio)
 * - Drawdown analysis
 * - Volatility measurements
 * - Win/loss statistics
 * - Duration tracking
 *
 * @note All calculations are based on the equity curve stored in the Record object.
 * @see Record class for data structure details
 */
class Metrics {
    private:
        // Private member variables could be added here for internal calculations

    public:
        Record record;  ///< Reference to the Record object containing simulation history

        // ===============================
        // Performance Metrics
        // ===============================

        double volatility = 0.0;  ///< Portfolio volatility (standard deviation of returns)
        double total_return = 0.0;  ///< Total return over the simulation period (as fraction)
        double annualized_return = 0.0;  ///< Annualized return based on total return (as fraction)
        double max_drawdown = 0.0;  ///< Maximum drawdown observed during the simulation (as fraction)
        double sharpe_ratio = 0.0;  ///< Sharpe ratio of the portfolio (risk-adjusted return)
        double sortino_ratio = 0.0;  ///< Sortino ratio of the portfolio (downside risk-adjusted return)
        double win_loss_ratio = 0.0;  ///< Win/loss ratio of executed trades

        // ===============================
        // Equity Metrics
        // ===============================

        double final_equity = 0.0;  ///< Final portfolio equity at simulation end
        double peak_equity = 0.0;  ///< Peak equity observed during the simulation

        // ===============================
        // Trade Statistics
        // ===============================

        size_t total_exected_positions = 0;  ///< Total number of positions executed (success + fail)

        // ===============================
        // Temporal Metrics
        // ===============================

        std::chrono::duration<double> duration;  ///< Duration of the simulation in seconds

        // ===============================
        // Constructors
        // ===============================

        /**
         * @brief Default constructor
         *
         * Initializes all metrics to zero values. The record must be set separately.
         */
        Metrics() = default;

        /**
         * @brief Constructor with Record object
         *
         * @param record The Record object containing simulation history data
         */
        Metrics(const Record &record) : record(record) {};

    /**
     * @brief Calculate and update all performance metrics based on the recorded history.
     *
     * This is the main entry point for computing all metrics. It performs calculations
     * in a specific order to ensure dependencies are met (e.g., Sharpe ratio must be
     * calculated before Sortino ratio).
     *
     * The calculation sequence is:
     * 1. Duration calculation
     * 2. Final equity extraction
     * 3. Annualized return calculation
     * 4. Win/loss ratio calculation
     * 5. Volatility calculation
     * 6. Total return calculation
     * 7. Maximum drawdown calculation
     * 8. Sharpe ratio calculation (prerequisite for Sortino)
     * 9. Sortino ratio calculation
     * 10. Total executed positions count
     *
     * @note This method modifies all metric member variables in place.
     * @warning Ensure the record object is properly initialized before calling.
     */
    void calculate() {
        this->calculate_duration();
        this->final_equity = this->record.equity.back();
        this->calculate_annualized_return();
        this->calculate_win_loss_ratio();
        this->calculate_volatility();
        this->calculate_total_return();
        this->calculate_max_drawdown();
        this->calculate_sharpe_ratio();    // It has to be computed before Sortino ratio
        this->calculate_sortino_ratio();

        this->total_exected_positions = this->record.success_count + this->record.fail_count;

    }

    /**
     * @brief Compute the portfolio's volatility.
     *
     * Volatility is defined as the standard deviation of periodic returns.
     * This metric provides a measure of how much the portfolio's value fluctuates
     * over time, serving as a key indicator of investment risk.
     *
     * The calculation uses the equity time series from the record to compute
     * period-to-period returns, then calculates their standard deviation.
     *
     * @note Requires a populated equity vector in the record object.
     * @post Updates the volatility member variable.
     */
    void calculate_volatility();

    /**
     * @brief Compute total return over the entire simulation period.
     *
     * Total return represents the overall percentage change in portfolio value
     * from the initial equity to the final equity, expressed as a fraction.
     * This is a fundamental measure of investment performance.
     *
     * Formula: (Final Equity - Initial Equity) / Initial Equity
     *
     * @note Requires equity data with at least two data points.
     * @post Updates the total_return member variable.
     * @return Total return as a fraction (e.g., 0.12 for +12% gain).
     */
    void calculate_total_return();

    /**
     * @brief Calculate the annualized (compounded) return from total return.
     *
     * Converts the total return into an equivalent annual rate of return,
     * accounting for the time period of the simulation. This allows for
     * comparison of strategies with different time horizons.
     *
     * Formula: (1 + total_return)^(365.25 * 24 * 3600 / duration_seconds) - 1
     *
     * @note Depends on total_return and duration being calculated first.
     * @post Updates the annualized_return member variable.
     * @return Annualized return as a fraction (e.g., 0.08 for +8% per year).
     */
    void calculate_annualized_return();

    /**
     * @brief Compute the maximum drawdown during the simulation.
     *
     * Maximum drawdown represents the largest peak-to-trough decline in portfolio value
     * as a fraction of the peak value. This metric is crucial for understanding the
     * worst-case scenario an investor would have experienced during the strategy's
     * execution period.
     *
     * The calculation finds the maximum running peak equity and computes the largest
     * percentage drop from any peak to a subsequent trough.
     *
     * @note Requires equity data to be available in the record.
     * @post Updates the max_drawdown member variable.
     * @return Maximum drawdown as a fraction (e.g., 0.25 for -25%).
     */
    void calculate_max_drawdown();

    /**
     * @brief Compute the Sharpe ratio (risk-adjusted return).
     *
     * The Sharpe ratio measures the excess return per unit of risk, calculated as
     * the ratio of the portfolio's excess return over the risk-free rate to its
     * standard deviation. This metric helps evaluate whether a portfolio's returns
     * are due to smart investment decisions or excessive risk-taking.
     *
     * Formula: (Portfolio Return - Risk-Free Rate) / Portfolio Standard Deviation
     *
     * @param risk_free_rate The risk-free rate of return (default = 0.0)
     * @note Requires volatility and annualized_return to be calculated first.
     * @post Updates the sharpe_ratio member variable.
     * @return Sharpe ratio (higher values indicate better risk-adjusted performance).
     */
    void calculate_sharpe_ratio(double risk_free_rate = 0.0);

    /**
     * @brief Compute the Sortino ratio (downside risk-adjusted return).
     *
     * The Sortino ratio is similar to the Sharpe ratio but only considers downside
     * volatility (negative returns) in the denominator. This provides a more accurate
     * measure of risk-adjusted returns since upside volatility is generally desired.
     *
     * Formula: (Portfolio Return - Risk-Free Rate) / Downside Deviation
     *
     * @param risk_free_rate The risk-free rate of return (default = 0.0)
     * @note Must be calculated after Sharpe ratio computation.
     * @post Updates the sortino_ratio member variable.
     * @return Sortino ratio (focuses on downside risk only).
     */
    void calculate_sortino_ratio(double risk_free_rate = 0.0);

    /**
     * @brief Calculate the win/loss ratio of executed trades.
     *
     * Win/loss ratio represents the proportion of successful trades to unsuccessful
     * trades. This metric provides insight into the strategy's hit rate and is
     * useful for understanding trade execution effectiveness.
     *
     * Formula: Number of Successful Trades / Number of Failed Trades
     *
     * @note Uses success_count and fail_count from the record object.
     * @post Updates the win_loss_ratio member variable.
     * @return Ratio of winning trades to losing trades (e.g., 1.5 for 60% win, 40% loss).
     */
    void calculate_win_loss_ratio();

    /**
     * @brief Compute the total duration of the simulation.
     *
     * Calculates the time span from the first timestamp to the last timestamp
     * in the simulation record. This duration is used for annualizing returns
     * and other time-based calculations.
     *
     * @note Requires timestamp data in the record object.
     * @post Updates the duration member variable.
     * @return Duration as a std::chrono::duration in seconds.
     */
    void calculate_duration();

    /**
     * @brief Calculate the peak equity observed during the simulation.
     *
     * Peak equity represents the highest portfolio value achieved at any point
     * during the simulation. This metric is useful for drawdown calculations
     * and understanding the strategy's best performance point.
     *
     * @note Requires equity data in the record object.
     * @post Updates the peak_equity member variable.
     * @return Peak equity value.
     */
    void calculate_peak_equity();

    /**
     * @brief Display the final performance metrics in human-readable form.
     *
     * Outputs all calculated metrics to the console in a formatted, easy-to-read
     * layout. This method is useful for debugging and performance analysis.
     *
     * @note Should be called after calculate() to ensure all metrics are computed.
     * @post Prints formatted output to stdout.
     */
    void display() const;
};
