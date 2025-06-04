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
            << position->get_price_difference()
            << "\n";
    }

    file.close();
}

void PositionCollection::open_positions(const ExitStrategy &exit_strategy) {

    for (size_t time_idx = 0; time_idx < this->market.dates.size(); time_idx++) {
        int signal_value = this->trade_signal[time_idx];

        if (signal_value == 0)
            continue;

        PositionPtr position;

        if (signal_value == 1)
            position = std::make_unique<Long>(exit_strategy, time_idx, this->market);

        else
            position = std::make_unique<Short>(exit_strategy, time_idx, this->market);

        positions.push_back(std::move(position));
    }
}

void PositionCollection::propagate_positions() {
    #pragma omp parallel for
    for (const auto& position : this->positions) {
        position->propagate();
    }

    this->terminate_open_positions();

    std::sort(
        this->positions.begin(),
        this->positions.end(),
        [](const PositionPtr& a, const PositionPtr& b) {return a->start_date < b->start_date;}
    );

    #pragma omp parallel for
    for (PositionPtr& position : this->positions)
        if (position->close_date == position->start_date) {
            position->display();
            throw std::runtime_error("Position cannot be closed at the same time it is opened!");
        }
}


void PositionCollection::terminate_open_positions() {
    for (const auto& position : this->positions)
        if (!position->is_closed) {
            position->close_at(this->market.dates.size() - 1);  // Set to last element of market
            position->is_closed = true;
        }

}


void PositionCollection::display() const {
    for (const PositionPtr& e : this->positions)
        e->display();
}

BasePosition* PositionCollection::__getitem__(const size_t idx) const {
    if (idx >= this->positions.size())
        throw std::out_of_range("Index out of range");
    return this->positions[idx].get();
}

inline std::vector<Long*> PositionCollection::get_long_positions(size_t count) const {
    std::vector<Long*> result;
    result.reserve(std::min(count, positions.size()));
    for (const auto& up : positions)
        if (auto ptr = dynamic_cast<Long*>(up.get())) {
            result.push_back(ptr);
            if (result.size() >= count) break;
        }

    return result;
}

inline std::vector<Short*> PositionCollection::get_short_positions(size_t count) const {
    std::vector<Short*> result;
    result.reserve(std::min(count, positions.size()));
    for (const auto& up : positions)
        if (auto ptr = dynamic_cast<Short*>(up.get())) {
            result.push_back(ptr);
            if (result.size() >= count) break;
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