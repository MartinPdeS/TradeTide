#include <fstream>
#include <iomanip>
#include "position_collection.h"

void PositionCollection::to_csv(const std::string& filepath) const {
    std::ofstream file(filepath);
    if (!file.is_open())
        throw std::runtime_error("Failed to open file for writing: " + filepath);

    // CSV header
    file << "start_date,close_date,entry_price,exit_price,lot_size,is_long,is_closed,profit_and_loss\n";

    for (const auto& position : positions) {
        auto format_time = [](const TimePoint& tp) -> std::string {
            std::time_t t = std::chrono::system_clock::to_time_t(tp);
            std::tm tm = *std::localtime(&t);
            std::ostringstream oss;
            oss << std::put_time(&tm, "%Y-%m-%d %H:%M:%S");
            return oss.str();
        };

        file
            << format_time(position->start_date) << ","
            << format_time(position->close_date) << ","
            << position->entry_price << ","
            << position->exit_price << ","
            << position->lot_size << ","
            << (position->is_long ? "True" : "False") << ","
            << (position->is_closed ? "True" : "False") << ","
            << position->calculate_profit_and_loss()
            << "\n";
    }

    file.close();
}

void PositionCollection::open_positions(){

    for (size_t idx = 0; idx < this->market.dates.size(); idx++){
        int signal_value = signal.trade_signal[idx];

        if (signal_value == 0)
            continue;

        PositionPtr position;
        std::unique_ptr<ExitStrategy> risk_manager_copy = exit_strategy_ptr->clone();

        if (signal_value == 1){
            double entry_price = (*this->market.ask.price)[idx];
            TimePoint start_date = this->market.dates[idx];
            position = std::make_unique<Long>(market, std::move(risk_manager_copy), entry_price, start_date, idx);
        }
        else {
            double entry_price = (*this->market.bid.price)[idx];
            TimePoint start_date = this->market.dates[idx];
            position = std::make_unique<Short>(market, std::move(risk_manager_copy), entry_price, start_date, idx);
        }

        positions.push_back(std::move(position));
    }
}

void PositionCollection::propagate_positions() {
    #pragma omp parallel for
    for (const auto& position : this->positions) {
        position->propagate();

    }
}


void PositionCollection::terminate_open_positions() {
    for (const auto& position : this->positions)
        if (!position->is_closed)
            position->set_close_condition(this->market.dates.size() - 1);  // Set to last element of market


        std::sort(
            this->positions.begin(),
            this->positions.end(),
            [](const PositionPtr& a, const PositionPtr& b) {return a->start_date < b->start_date;}
        );
}


void PositionCollection::display(){
    for (const PositionPtr& e : this->positions)
        e->display();
}


inline std::vector<Long*> PositionCollection::get_long_positions(size_t count) const {
    std::vector<Long*> result;
    result.reserve(std::min(count, positions.size()));
    for (const auto& up : positions) {
        if (auto ptr = dynamic_cast<Long*>(up.get())) {
            result.push_back(ptr);
            if (result.size() >= count) break;
        }
    }
    return result;
}

inline std::vector<Short*> PositionCollection::get_short_positions(size_t count) const {
    std::vector<Short*> result;
    result.reserve(std::min(count, positions.size()));
    for (const auto& up : positions) {
        if (auto ptr = dynamic_cast<Short*>(up.get())) {
            result.push_back(ptr);
            if (result.size() >= count) break;
        }
    }
    return result;
}

inline std::vector<BasePosition*> PositionCollection::get_all_positions(size_t count) const {
    std::vector<BasePosition*> result;
    result.reserve(std::min(count, positions.size()));
    for (const auto& up : positions) {
        result.push_back(up.get());
        if (result.size() >= count) break;
    }
    return result;
}