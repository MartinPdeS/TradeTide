#include "metrics.h"


void Metrics::calculate_annualized_return() {
    double fractional_years = std::chrono::duration_cast<std::chrono::seconds>(this->duration).count() / 31557600.0;

    this->annualized_return = std::pow(1.0 + this->total_return, 1.0 / fractional_years) - 1.0;
}


void Metrics::calculate_total_return() {
    this->total_return = (this->record.equity.back() - this->record.equity.front()) / this->record.equity.front();
}


void Metrics::calculate_volatility() {
    if (this->record.equity.size() < 2) {
        this->volatility = 0.0; // No volatility if we have less than 2 data points
        return;
    }

    std::vector<double> returns;
    for (size_t i = 1; i < this->record.equity.size(); ++i) {
        double r = (this->record.equity[i] - this->record.equity[i - 1]) / this->record.equity[i - 1];
        returns.push_back(r);
    }

    double mean = std::accumulate(returns.begin(), returns.end(), 0.0) / returns.size();
    double variance = 0.0;
    for (double r : returns)
        variance += (r - mean) * (r - mean);

    variance /= returns.size();

    this->volatility = std::sqrt(variance);
}

void Metrics::calculate_sharpe_ratio(double risk_free_rate) {
    if (this->record.equity.size() < 2) {
        this->sharpe_ratio = 0.0;
        return;
    }

    std::vector<double> returns;
    for (size_t i = 1; i < this->record.equity.size(); ++i) {
        double r = (this->record.equity[i] - this->record.equity[i - 1]) / this->record.equity[i - 1];
        returns.push_back(r - risk_free_rate);
    }

    double mean = std::accumulate(returns.begin(), returns.end(), 0.0) / returns.size();
    double variance = 0.0;
    for (double r : returns) variance += (r - mean) * (r - mean);
    variance /= returns.size();

    this->sharpe_ratio = mean / std::sqrt(variance);
}

void Metrics::calculate_sortino_ratio(double risk_free_rate) {
    if (this->record.equity.size() < 2) {
        this->sortino_ratio = 0.0;
        return;
    }

    std::vector<double> downside_returns;
    for (size_t i = 1; i < this->record.equity.size(); ++i) {
        double r = (this->record.equity[i] - this->record.equity[i - 1]) / this->record.equity[i - 1];
        double excess = r - risk_free_rate;
        if (excess < 0) downside_returns.push_back(excess);
    }

    if (downside_returns.empty()) {
        this->sortino_ratio = 0.0;
        return;
    }

    this->calculate_sharpe_ratio(risk_free_rate);

    double mean_excess_return = this->sharpe_ratio; // re-use numerator
    double stddev_downside = 0.0;
    for (double r : downside_returns)
        stddev_downside += r * r;

    stddev_downside = std::sqrt(stddev_downside / downside_returns.size());

    this->sortino_ratio = mean_excess_return / stddev_downside;
}


void Metrics::calculate_duration() {
    this->duration = this->record.time.back() - this->record.time.front();
}

void Metrics::calculate_max_drawdown() {
    double peak = this->record.equity.front();
    double max_drawdown = 0.0;

    for (double equity : this->record.equity) {
        peak = std::max(peak, equity);
        double drawdown = (peak - equity) / peak;
        max_drawdown = std::max(max_drawdown, drawdown);
    }
    this->max_drawdown = max_drawdown;
}


void Metrics::calculate_win_loss_ratio() {
    size_t total_positions = this->record.success_count + this->record.fail_count;

    if (total_positions == 0) {
        this->win_loss_ratio = 0.0; // No positions to calculate ratio
        return;
    }

    this->win_loss_ratio = this->record.success_count / static_cast<double>(total_positions);
}

void Metrics::calculate_peak_equity() {
    this->peak_equity = *std::max_element(this->record.equity.begin(), this->record.equity.end());
}

void Metrics::display() const {
    // Extract days, hours, minutes
    using namespace std::chrono;

    typedef std::chrono::duration<int, std::ratio<86400>> Days;
    const Days days = std::chrono::duration_cast<Days>(duration);
    const std::chrono::hours hours = std::chrono::duration_cast<std::chrono::hours>(duration - days);
    const std::chrono::minutes minutes = std::chrono::duration_cast<std::chrono::minutes>(duration - days - hours);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "\nPortfolio Summary:\n";
    std::cout << "------------------\n";
    std::cout << "Final Equity:          " << this->final_equity << "\n";
    std::cout << "Peak Equity:           " << this->peak_equity << "\n";
    std::cout << "Total Return:          " << this->total_return * 100 << " %\n";
    std::cout << "Annualized Return:     " << this->annualized_return * 100 << " %\n";
    std::cout << "Max Drawdown:          " << this->max_drawdown * 100 << " %\n";
    std::cout << "Sharpe Ratio:          " << this->sharpe_ratio << "\n";
    std::cout << "Sortino Ratio:         " << this->sortino_ratio << "\n";
    std::cout << "Win/Loss Ratio:        " << this->win_loss_ratio << "\n";
    std::cout << "Volatility:            " << this->volatility * 100 << " %\n";
    std::cout << "Positions Executed:    " << this->total_exected_positions << "\n";
    std::cout << "Market Duration:       "
              << days.count() << "d "
              << hours.count() << "h "
              << minutes.count() << "m\n"
              << "Position Computation:  " << std::chrono::duration_cast<std::chrono::milliseconds>(this->record.computation_duration).count() << " ms\n"
              << "Portfolio Computation: " << std::chrono::duration_cast<std::chrono::milliseconds>(this->record.computation_duration).count() << " ms\n";
    std::cout << "------------------\n"
    ;
}