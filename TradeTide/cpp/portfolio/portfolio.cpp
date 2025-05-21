#include "portfolio.h"
#include <iostream>
#include <iomanip>

double Portfolio::final_equity() const {
    return this->capital_management.current_equity;
}

double Portfolio::peak_equity() const {
    if (this->equity_history.empty())
        return this->capital_management.initial_capital;

    return *std::max_element(this->equity_history.begin(), this->equity_history.end());
}

std::vector<double> Portfolio::equity_curve() const {
    return this->equity_history;
}

void Portfolio::simulate() {
    this->reset_state();

    const auto& dates = this->position_collection.get_market().dates;
    const auto& all_positions = this->position_collection.positions;

    size_t position_index = 0;
    this->capital_management.position_count = 0;

    for (const TimePoint& current_time : dates) {
        this->current_time = current_time;

        // Finalize positions whose close_date <= current_time
        for (auto it = this->active_positions.begin(); it != this->active_positions.end();) {
            const PositionPtr& pos = *it;

            if (pos->close_date <= current_time) {
                this->capital_management.current_equity += pos->calculate_profit_and_loss();
                this->capital_management.position_count--;
                it = this->active_positions.erase(it);
            }
            else
                ++it;
        }

        // ➕ Try to activate new positions starting now
        while (position_index < all_positions.size() && all_positions[position_index]->start_date == current_time) {

        const PositionPtr& pos = all_positions[position_index];

        // If we can't open more positions now, skip this one (but advance index!)
        if (this->capital_management.position_count >= this->capital_management.max_concurrent_positions) {
            ++position_index;
            continue;
        }

        // Compute lot size
        this->capital_management.compute_lot_size(*pos);

        // Skip if not enough capital to open
        if (pos->lot_size == 0.0) {
            ++position_index;
            continue;
        }

        // Accept position
        this->capital_management.position_count++;
        this->active_positions.push_back(pos);
        this->selected_positions.push_back(pos);
        this->executed_positions.push_back(pos);

        ++position_index;
    }


        // Track portfolio state at this time
        this->open_position_count.push_back(this->active_positions.size());
        this->equity_history.push_back(this->capital_management.current_equity);
    }

    // 📌 Close all remaining positions at end
    for (const auto& pos : this->active_positions) {
        this->capital_management.current_equity += pos->calculate_profit_and_loss();
    }

    std::cout<<"this->selected_positions.size() = "<<this->selected_positions.size()<<std::endl;
    this->active_positions.clear();
}


void Portfolio::reset_state() {
    this->capital_management.current_equity = this->capital_management.initial_capital;
    this->selected_positions.clear();
    this->executed_positions.clear();
    this->equity_history.clear();
    this->open_position_count.clear();
}



void Portfolio::display() const {
    for (const PositionPtr& position : this->selected_positions)
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
    std::cout << "Positions Executed:    " << this->executed_positions.size() << "\n";

    const auto seconds = std::chrono::duration_cast<std::chrono::seconds>(duration).count();
    const int days = static_cast<int>(seconds / 86400);
    const int hours = static_cast<int>((seconds % 86400) / 3600);
    const int minutes = static_cast<int>((seconds % 3600) / 60);

    std::cout << "Simulation Duration:   " << days << "d " << hours << "h " << minutes << "m\n";
}



void Portfolio::compute_open_position_count_over_time() {
    const std::vector<TimePoint>& dates = this->position_collection.get_market().dates;

    this->open_position_count.clear();
    this->open_position_count.reserve(dates.size());

    size_t count;
    for (size_t i = 0; i < dates.size(); ++i) {
        count = 0;
        for (const PositionPtr& position : this->selected_positions)
            if (position->is_open(dates[i]))
                count++;

        this->open_position_count.push_back(count);
    }
}

void Portfolio::compute_equity_over_time() {
    const std::vector<TimePoint>& dates = this->position_collection.get_market().dates;

    this->equity_history.clear();
    this->equity_history.reserve(dates.size());

    for (size_t i = 0; i < dates.size(); ++i) {
        this->current_time = dates[i];
        double equity = this->capital_management.initial_capital;

        for (const PositionPtr& position : this->selected_positions) {
            if (position->is_closed && position->close_date <= current_time) {
                equity += position->calculate_profit_and_loss();
            }
        }

        this->equity_history.push_back(equity);
    }
}

const std::vector<TimePoint>& Portfolio::get_market_dates() const {
    return this->position_collection.get_market().dates;
}

std::vector<BasePosition*> Portfolio::get_positions(size_t count) const {
    if (count == std::numeric_limits<size_t>::max()) {
        count = this->selected_positions.size();
    }

    std::vector<BasePosition*> result;
    result.reserve(std::min(count, this->selected_positions.size()));

    for (const auto& up : this->selected_positions) {
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
    double peak = this->equity_history.front();
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

    for (const auto& position : this->selected_positions) {
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

