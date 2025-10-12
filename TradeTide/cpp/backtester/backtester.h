#pragma once

#include <vector>
#include <chrono>
#include <string>
#include <iostream>
#include <iomanip>  // for std::setw

#include "../position_collection/position_collection.h"
#include "../strategy/strategy.h"
#include "../exit_strategy/exit_strategy.h"
#include "../market/market.h"
#include "../metrics/metrics.h"
#include "../portfolio/portfolio.h"
#include "../capital_management/capital_management.h"


constexpr int width_label = 35;
constexpr int width_value = 20;

class ScopedTimer {
public:
    using Clock = std::chrono::high_resolution_clock;

    ScopedTimer(const std::string& name, std::chrono::microseconds& output_duration)
        : label(name), output(output_duration), start(Clock::now()) {}

    ~ScopedTimer() {
        auto end = Clock::now();
        output = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    }

private:
    std::string label;
    std::chrono::microseconds& output;
    Clock::time_point start;
};


class Backtester {
public:
    Strategy strategy;
    ExitStrategy &exit_strategy;
    Market market;
    BaseCapitalManagement &capital_management;
    PositionCollection position_collection;
    Portfolio portfolio;

    // Timers for various phases
    std::chrono::microseconds trade_signal_computation_run_time;
    std::chrono::microseconds open_position_run_time;
    std::chrono::microseconds propagate_run_time;
    std::chrono::microseconds portfolio_run_time;

    /*
    @brief Construct a Backtester with strategy, exit strategy, market data, and capital management
    @param strategy Reference to the trading strategy to be tested.
    @param exit_strategy Reference to the exit strategy to be used for position management.
    @param market Reference to the market data to be used in the backtest.
    @param capital_management Reference to the capital management strategy for position sizing.
    @param debug_mode Enables debug output for development purposes.
    */
    Backtester(Strategy& strategy, ExitStrategy& exit_strategy, Market& market, BaseCapitalManagement& capital_management, const bool debug_mode);

    /*
    @brief Execute the backtest.
    @details This method runs the complete backtesting process, including generating trade signals,
    opening and propagating positions, and simulating the portfolio performance.
    */
    void run();

    /*
    @brief Display the backtest results.
    @details This method presents the key outcomes of the backtest in a user-friendly format.
    */
    void display() const;

    /*
    @brief Print the performance metrics of the backtest.
    @details This method outputs key performance indicators such as total return, maximum drawdown,
    and other relevant metrics to evaluate the effectiveness of the trading strategy.
    */
    void print_performance();

    /*
    @brief Print a summary of the backtest results.
    @details This method provides an overview of the backtest performance, including key metrics
    and execution times.
    */
    void print_summary();

    /*
    Print basic information about the backtest.
    @brief This method outputs key details about the backtest including
    */
    void print_basic_info() const;

    /*
    @brief Print the execution times for each phase of the backtest.
    @details This method outputs the time taken for trade signal computation, opening positions,
    propagating positions, and the overall portfolio simulation runtime. The times are displayed
    in microseconds for precision.
    */
    void print_run_times() const;

private:
    /*
    @brief Print the header for a section.
    @details This method outputs a centered header with a title and surrounding
    lines for visual separation.
    */
    void print_header(const std::string& title) const {
        std::cout << "\n" << std::string(60, '=') << "\n";
        std::cout << std::setw((60 + title.size()) / 2)
                  << std::right << title << "\n";
        std::cout << std::string(60, '=') << "\n";
    };

    /*
    @brief Print a section header.
    @details This method outputs a title for a section and a line separator.
    */
    void print_section(const std::string& title) const {
        std::cout << "\n" << title << "\n"
                  << std::string(title.size(), '-') << "\n";
    };

    /*
    @brief Print a labeled line with a value.
    @details This method formats and outputs a label and its corresponding value
    in a structured manner for better readability.
    */
    void print_line(const std::string& label, const std::string& value) const {
        std::cout << std::setw(width_label) << std::left << label
                  << std::setw(width_value) << std::right << value << "\n";
    };

};
