#include "portfolio.h"




using Duration = std::chrono::system_clock::duration;
using TimePoint = std::chrono::system_clock::time_point;

double Portfolio::final_equity() const {
    return this->state.equity;
}

double Portfolio::peak_equity() const {
    return *std::max_element(this->record.equity.begin(), this->record.equity.end());
}

void Portfolio::close_position(PositionPtr& position, const size_t &position_idx) {
    this->active_positions.erase(this->active_positions.begin() + position_idx);
    this->state.number_of_concurrent_positions -= 1;
    this->state.capital += position->exit_price * position->lot_size;
    position->is_closed = true;
}

void Portfolio::open_position(PositionPtr& position, const BaseCapitalManagement &capital_management) {
    this->active_positions.push_back(position);
    this->selected_positions.push_back(position);
    this->executed_positions.push_back(position);

    position->lot_size = capital_management.compute_lot_size(*position);

    this->state.number_of_concurrent_positions += 1;
    this->state.capital -= position->entry_price * position->lot_size;
    position->is_closed = false;
}

void Portfolio::try_close_positions(BaseCapitalManagement& capital_management) {
    for (size_t i = 0; i < this->active_positions.size(); i++) {
        PositionPtr& position = this->active_positions[i];

        // Attempt to close position
        if (position->close_date == this->state.current_date && capital_management.can_close_position(position))
            this->close_position(position, i);

    }
}

void Portfolio::try_open_positions(BaseCapitalManagement& capital_management) {
    while (this->state.position_index < this->position_collection.positions.size()) {

        // If we reached the end of positions, stop trying to open new ones
        if (this->position_collection.positions[this->state.position_index]->start_date != this->state.current_date)
            break;


        PositionPtr& position = this->position_collection.positions[this->state.position_index];

        // If we can't open more positions now, skip this one (but advance index!)
        if (capital_management.can_open_position(position))
            this->open_position(position, capital_management);

        ++this->state.position_index;
    }

}

void Portfolio::simulate(BaseCapitalManagement& capital_management) {
    this->selected_positions.clear();
    this->executed_positions.clear();
    this->active_positions.clear();

    this->state = State(this->position_collection.market, capital_management.initial_capital);
    capital_management.state  = &this->state;

    for (PositionPtr& position : this->position_collection.positions)
        position->is_closed = false;

    for (size_t time_idx = 0; time_idx < this->position_collection.market.dates.size(); time_idx ++) {
        this->state.update_time_idx(time_idx);

        // Try to close opened positions
        this->try_close_positions(capital_management);

        // Try to activate new positions starting now
        this->try_open_positions(capital_management);

        if (time_idx == this->position_collection.market.dates.size() - 1)
            this->terminate_open_positions();

        state.capital_at_risk = this->calculate_capital_at_risk();
        state.equity = this->calculate_equity();
        this->record.update();
    }
}


void Portfolio::terminate_open_positions() {
    for (const auto& position : this->active_positions) {
        this->state.number_of_concurrent_positions -= 1;
        this->state.capital += position->exit_price * position->lot_size;
        position->is_closed = true;
    }

    this->active_positions.clear();
}


void Portfolio::display() const {
    for (const PositionPtr& position : this->selected_positions)
        position->display();

    const double total_return       = this->calculate_total_return();
    const double annualized_return  = this->calculate_annualized_return(total_return);
    const double max_drawdown       = this->calculate_max_drawdown();
    const double sharpe             = this->calculate_sharpe_ratio();
    const double sortino            = this->calculate_sortino_ratio();
    const double win_loss           = this->calculate_win_loss_ratio();
    const double volatility         = this->calculate_volatility();
    const std::chrono::duration<double> duration = this->calculate_duration();

    // Extract days, hours, minutes
    using namespace std::chrono;

    typedef std::chrono::duration<int, std::ratio<86400>> Days;
    const Days days = std::chrono::duration_cast<Days>(duration);
    const std::chrono::hours hours = std::chrono::duration_cast<std::chrono::hours>(duration - days);
    const std::chrono::minutes minutes = std::chrono::duration_cast<std::chrono::minutes>(duration - days - hours);

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
    std::cout << "Duration:              "
              << days.count() << "d "
              << hours.count() << "h "
              << minutes.count() << "m\n";
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
    return (this->record.equity.back() - this->record.equity.front()) / this->record.equity.front();
}

double Portfolio::calculate_annualized_return(double total_return) const {

    std::chrono::duration<double> duration = this->calculate_duration();

    double fractional_years = std::chrono::duration_cast<std::chrono::seconds>(duration).count() / 31557600.0;

    return std::pow(1.0 + total_return, 1.0 / fractional_years) - 1.0;
}

std::chrono::duration<double> Portfolio::calculate_duration() const {
    const auto& dates = this->get_market_dates();
    if (dates.empty()) return std::chrono::duration<double>(0);

    return dates.back() - dates.front();
}

double Portfolio::calculate_max_drawdown() const {
    double peak = this->record.equity.front();
    double max_drawdown = 0.0;

    for (double equity : this->record.equity) {
        peak = std::max(peak, equity);
        double drawdown = (peak - equity) / peak;
        max_drawdown = std::max(max_drawdown, drawdown);
    }
    return max_drawdown;
}

double Portfolio::calculate_sharpe_ratio(double risk_free_rate) const {
    if (this->record.equity.size() < 2) return 0.0;

    std::vector<double> returns;
    for (size_t i = 1; i < this->record.equity.size(); ++i) {
        double r = (this->record.equity[i] - this->record.equity[i - 1]) / this->record.equity[i - 1];
        returns.push_back(r - risk_free_rate);
    }

    double mean = std::accumulate(returns.begin(), returns.end(), 0.0) / returns.size();
    double variance = 0.0;
    for (double r : returns) variance += (r - mean) * (r - mean);
    variance /= returns.size();

    return mean / std::sqrt(variance);
}

double Portfolio::calculate_sortino_ratio(double risk_free_rate) const {
    if (this->record.equity.size() < 2) return 0.0;

    std::vector<double> downside_returns;
    for (size_t i = 1; i < this->record.equity.size(); ++i) {
        double r = (this->record.equity[i] - this->record.equity[i - 1]) / this->record.equity[i - 1];
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
        double pnl = position->get_price_difference();
        if (pnl > 0) ++wins;
        else if (pnl < 0) ++losses;
    }

    if (losses == 0) return (wins > 0 ? std::numeric_limits<double>::infinity() : 0.0);
    return static_cast<double>(wins) / losses;
}

double Portfolio::calculate_volatility() const {
    if (this->record.equity.size() < 2) return 0.0;

    std::vector<double> returns;
    for (size_t i = 1; i < this->record.equity.size(); ++i) {
        double r = (this->record.equity[i] - this->record.equity[i - 1]) / this->record.equity[i - 1];
        returns.push_back(r);
    }

    double mean = std::accumulate(returns.begin(), returns.end(), 0.0) / returns.size();
    double variance = 0.0;
    for (double r : returns) variance += (r - mean) * (r - mean);
    variance /= returns.size();

    return std::sqrt(variance);
}

double Portfolio::calculate_capital_at_risk() const {
    double total_risk = 0.0;

    for (const PositionPtr& position : this->active_positions)
        total_risk += std::abs(position->entry_price - position->exit_strategy->stop_loss_price) * position->lot_size;

    return total_risk;
}

double Portfolio::calculate_equity() const {
    double equity = this->state.capital;

    for (const PositionPtr& position : this->active_positions)
        if (!position->is_closed)
            equity += position->get_closing_value_at(this->state.time_idx);


    return equity;
}