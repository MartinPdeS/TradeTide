#pragma once

#include <vector>
#include <chrono>
#include "../record/record.h"


class Metrics {
    public:
        Record record;  ///< Reference to the Record object containing simulation history

        double volatility = 0.0;  ///< Portfolio volatility
        double total_return = 0.0;  ///< Total return over the simulation period
        double annualized_return = 0.0;  ///< Annualized return based on total return
        double max_drawdown = 0.0;  ///< Maximum drawdown observed during the simulation
        double sharpe_ratio = 0.0;  ///< Sharpe ratio of the portfolio
        double sortino_ratio = 0.0;  ///< Sortino ratio of the portfolio
        double win_loss_ratio = 0.0;  ///< Win/loss ratio of executed trades
        double final_equity = 0.0;  ///< Final portfolio equity
        double peak_equity = 0.0;  ///< Peak equity observed during the simulation
        size_t total_exected_positions = 0;  ///< Total number of positions executed
        std::chrono::duration<double, std::milli> computation_duration;  ///< Duration of the computation in milliseconds

        std::chrono::duration<double> duration;  ///< Duration of the simulation

    Metrics() = default;
    Metrics(const Record &record) : record(record) {};

    /**
     * @brief Calculate and update all performance metrics based on the recorded history.
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

        this->computation_duration = std::chrono::duration_cast<std::chrono::milliseconds>(this->record.end_computation_time - this->record.start_computation_time);

    }

    /**
     * @brief Compute the portfolio's volatility.
     *
     * Volatility is defined as the standard deviation of periodic returns.
     *
     * @return Volatility (e.g., 0.05 for 5%).
     */
    void calculate_volatility();

    /**
     * @brief Compute total return over the entire simulation period.
     *
     * @return Total return as a fraction (e.g., 0.12 for +12% gain).
     */
    void calculate_total_return();

    /**
     * @brief Calculate the annualized (compounded) return from total return.
     *
     * @param total_return The total return (from calculate_total_return).
     * @return Annualized return as a fraction (e.g., 0.08 for +8% per year).
     */
    void calculate_annualized_return();

    /**
     * @brief Compute the maximum drawdown during the simulation.
     *
     * Max drawdown is the largest peak-to-trough equity drop as a fraction of the peak.
     *
     * @return Maximum drawdown (e.g., 0.25 for -25%).
     */
    void calculate_max_drawdown();

    /**
     * @brief Compute the Sharpe ratio (risk-adjusted return).
     *
     * @param risk_free_rate Optional risk-free rate (default = 0).
     * @return Sharpe ratio (mean excess return divided by standard deviation of returns).
     */
    void calculate_sharpe_ratio(double risk_free_rate = 0.0);

    /**
     * @brief Compute the Sortino ratio (risk-adjusted return using downside risk).
     *
     * @param risk_free_rate Optional risk-free rate (default = 0).
     * @return Sortino ratio (mean excess return divided by downside deviation).
     */
    void calculate_sortino_ratio(double risk_free_rate = 0.0);

    /**
     * @brief Calculate the win/loss ratio of executed trades.
     *
     * @return Ratio of winning trades to losing trades (e.g., 1.5 for 60% win, 40% loss).
     */
    void calculate_win_loss_ratio();

    /**
     * @brief Compute the total duration of the simulation.
     *
     * @return Duration as a std::chrono::duration in seconds.
     */
    void calculate_duration();

    /**
     * @brief Calculate the peak equity observed during the simulation.
     *
     * Peak equity is the highest value of portfolio equity at any point in time.
     *
     * @return Peak equity value.
     */
    void calculate_peak_equity();

    /**
     * @brief Display the final performance metrics in human-readable form.
     */
    void display() const;
};
