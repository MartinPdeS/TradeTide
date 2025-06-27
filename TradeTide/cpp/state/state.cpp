#include "state.h"

State::State(const Market &market, double capital): market(&market)
{
    this->n_elements = market.dates.size();
    this->initialize(capital);
    this->dates = &market.dates;
}

void State::initialize(const double capital) {
    this->time_idx = 0;
    this->position_index = 0;
    this->number_of_concurrent_positions = 0;
    this->equity = capital;
    this->capital = capital;
}


void State::display() const {
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Current State:\n";
    std::cout << "--------------\n";
    std::cout << "Equity:                     " << this->equity << "\n";
    std::cout << "Capital at Risk:            " << this->capital_at_risk << "\n";
    std::cout << "Concurrent Open Positions:  " << this->number_of_concurrent_positions << "\n";
    std::time_t t = std::chrono::system_clock::to_time_t(this->current_date);
    std::cout << "Current Time:               " << std::put_time(std::localtime(&t), "%Y-%m-%d %H:%M:%S") << "\n\n";
}

void State::update_time_idx(const size_t time_idx) {
    this->time_idx = time_idx;
    this->current_date = this->market->dates[time_idx];

    this->ask.open = this->market->ask.open[time_idx];
    this->ask.low  = this->market->ask.low[time_idx];
    this->ask.high = this->market->ask.high[time_idx];
    this->ask.close = this->market->ask.close[time_idx];

    this->bid.open = this->market->bid.open[time_idx];
    this->bid.low  = this->market->bid.low[time_idx];
    this->bid.high = this->market->bid.high[time_idx];
    this->bid.close = this->market->bid.close[time_idx];
}