#include "portfolio.h"
#include <iostream>
#include <iomanip>

double Portfolio::final_equity() const {
    return this->state.equity;
}

double Portfolio::peak_equity() const {
    if (this->equity_history.empty())
        return this->capital_management.initial_capital;

    return *std::max_element(this->equity_history.begin(), this->equity_history.end());
}

void Portfolio::simulate() {
    this->capital_management.reset_state();
    this->capital_management.state = &this->state;
    const auto& all_positions = this->position_collection.positions;

    size_t position_index = 0;
    this->state.number_of_concurrent_positions = 0;
    this->state.equity = this->capital_management.initial_capital;

    for (const TimePoint& current_time : this->position_collection.market.dates) {
        this->state.time = current_time;
        this->state.capital_at_risk = this->calculate_capital_at_risk_at(current_time);

        for (size_t i = 0; i < this->capital_management.active_positions.size(); ) {
            const PositionPtr& pos = this->capital_management.active_positions[i];

            // Skip positions that are not closing at this current_time
            if (pos->close_date > this->state.time) {
                ++i;
                continue;
            }

            // Attempt to close position
            bool close_success = this->capital_management.try_close_position(pos);
            if (close_success) {
                this->capital_management.active_positions.erase(this->capital_management.active_positions.begin() + i);
                this->state.number_of_concurrent_positions -= 1;
            }
            else
                ++i;

        }

        // ➕ Try to activate new positions starting now
        while (position_index < all_positions.size() && all_positions[position_index]->start_date == current_time) {

            const PositionPtr& pos = all_positions[position_index];

            // If we can't open more positions now, skip this one (but advance index!)
            bool open_success = this->capital_management.try_open_position(pos);

            if (open_success)
                this->state.number_of_concurrent_positions += 1;

            ++position_index;
        }

        this->state.update();
    }

    // Close all remaining positions at end
    for (const auto& pos : this->capital_management.active_positions)
        this->state.equity += pos->calculate_profit_and_loss();

    this->capital_management.active_positions.clear();
}


void Portfolio::display() const {
    for (const PositionPtr& position : this->capital_management.selected_positions)
        position->display();

    const double total_return = this->calculate_total_return();
    const double annualized_return = this->calculate_annualized_return(total_return);
    const double max_drawdown = this->calculate_max_drawdown();
    const double sharpe = this->calculate_sharpe_ratio();
    const double sortino = this->calculate_sortino_ratio();
    const double win_loss = this->calculate_win_loss_ratio();
    const double volatility = this->calculate_volatility();
    const auto duration = this->calculate_duration();

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "\nPortfolio Summary:\n";
    std::cout << "------------------\n";
    std::cout << "Final Equity:          " << this->final_equity() << "\n";
    std::cout << "Peak Equity:           " << this->peak_equity() << "\n";
    std::cout << "Total Return:          " << total_return * 100 << " %\n";
    std::cout << "Annualized Return:     " << annualized_return * 100 << " %\n";
    std::cout << "Max Drawdown:          " << max_drawdown * 100 << " %\n";
    std::cout << "Sharpe Ratio:          " << sharpe << "\n";
    std::cout << "Sortino Ratio:         " << sortino << "\n";
    std::cout << "Win/Loss Ratio:        " << win_loss << "\n";
    std::cout << "Volatility:            " << volatility * 100 << " %\n";
    std::cout << "Positions Executed:    " << this->capital_management.executed_positions.size() << "\n";
    std::cout << "Duration:              " << duration << "\n";
}


const std::vector<TimePoint>& Portfolio::get_market_dates() const {
    return this->position_collection.get_market().dates;
}

std::vector<BasePosition*> Portfolio::get_positions(size_t count) const {
    if (count == std::numeric_limits<size_t>::max()) {
        count = this->capital_management.selected_positions.size();
    }

    std::vector<BasePosition*> result;
    result.reserve(std::min(count, this->capital_management.selected_positions.size()));

    for (const auto& up : this->capital_management.selected_positions) {
        result.push_back(up.get());
        if (result.size() >= count) break;
    }

    return result;
}

double Portfolio::calculate_total_return() const {
    return (this->final_equity() - this->capital_management.initial_capital) / this->capital_management.initial_capital;
}

double Portfolio::calculate_annualized_return(double total_return) const {
    auto duration = this->calculate_duration().count() / (365.25 * 24 * 60 * 60); // in years
    return std::pow(1.0 + total_return, 1.0 / duration) - 1.0;
}

std::chrono::duration<double> Portfolio::calculate_duration() const {
    const auto& dates = this->get_market_dates();
    if (dates.empty()) return std::chrono::duration<double>(0);

    return dates.back() - dates.front();
}

double Portfolio::calculate_max_drawdown() const {
    double peak = this->state.equity_history.front();
    double max_drawdown = 0.0;

    for (double equity : this->equity_history) {
        peak = std::max(peak, equity);
        double drawdown = (peak - equity) / peak;
        max_drawdown = std::max(max_drawdown, drawdown);
    }
    return max_drawdown;
}

double Portfolio::calculate_sharpe_ratio(double risk_free_rate) const {
    if (this->equity_history.size() < 2) return 0.0;

    std::vector<double> returns;
    for (size_t i = 1; i < this->equity_history.size(); ++i) {
        double r = (this->equity_history[i] - this->equity_history[i - 1]) / this->equity_history[i - 1];
        returns.push_back(r - risk_free_rate);
    }

    double mean = std::accumulate(returns.begin(), returns.end(), 0.0) / returns.size();
    double variance = 0.0;
    for (double r : returns) variance += (r - mean) * (r - mean);
    variance /= returns.size();

    return mean / std::sqrt(variance);
}

double Portfolio::calculate_sortino_ratio(double risk_free_rate) const {
    if (this->equity_history.size() < 2) return 0.0;

    std::vector<double> downside_returns;
    for (size_t i = 1; i < this->equity_history.size(); ++i) {
        double r = (this->equity_history[i] - this->equity_history[i - 1]) / this->equity_history[i - 1];
        double excess = r - risk_free_rate;
        if (excess < 0) downside_returns.push_back(excess);
    }

    if (downside_returns.empty()) return 0.0;

    double mean_excess_return = this->calculate_sharpe_ratio(risk_free_rate); // re-use numerator
    double stddev_downside = 0.0;
    for (double r : downside_returns)
        stddev_downside += r * r;
    stddev_downside = std::sqrt(stddev_downside / downside_returns.size());

    return mean_excess_return / stddev_downside;
}

double Portfolio::calculate_win_loss_ratio() const {
    size_t wins = 0, losses = 0;

    for (const auto& position : this->capital_management.selected_positions) {
        if (!position->is_closed) continue;
        double pnl = position->calculate_profit_and_loss();
        if (pnl > 0) ++wins;
        else if (pnl < 0) ++losses;
    }

    if (losses == 0) return (wins > 0 ? std::numeric_limits<double>::infinity() : 0.0);
    return static_cast<double>(wins) / losses;
}

double Portfolio::calculate_equity() const {
    return this->final_equity();
}

double Portfolio::calculate_volatility() const {
    if (this->equity_history.size() < 2) return 0.0;

    std::vector<double> returns;
    for (size_t i = 1; i < this->equity_history.size(); ++i) {
        double r = (this->equity_history[i] - this->equity_history[i - 1]) / this->equity_history[i - 1];
        returns.push_back(r);
    }

    double mean = std::accumulate(returns.begin(), returns.end(), 0.0) / returns.size();
    double variance = 0.0;
    for (double r : returns) variance += (r - mean) * (r - mean);
    variance /= returns.size();

    return std::sqrt(variance);
}

double Portfolio::calculate_capital_at_risk_at(const TimePoint& current_time) const {
    double total_risk = 0.0;

    for (const PositionPtr& position : this->capital_management.active_positions) {
        if (position->is_open(current_time)) {
            const double risk = std::abs(position->entry_price - position->exit_strategy->stop_loss_price) * position->lot_size;

            total_risk += risk;
        }
    }

    return total_risk;
}