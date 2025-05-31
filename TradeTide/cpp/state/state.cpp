#include "state.h"

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