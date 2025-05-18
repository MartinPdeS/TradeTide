#include "position_collection.h"


void PositionCollection::open_positions(){

    for (size_t idx = 0; idx < this->market.dates.size(); idx++){
        int signal_value = signal.trade_signal[idx];

        if (signal_value == 0)
            continue;

        PositionPtr position;
        std::unique_ptr<ExitStrategy> risk_manager_copy = exit_strategy.clone();

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

void PositionCollection::close_positions(){
    for (const auto& position : this->positions)
        position->propagate();
}


void PositionCollection::terminate_open_positions() {
    for (const auto& position : this->positions)
        if (!position->is_closed)
            position->close(this->market.dates.size() - 1);  // Set to last element of market

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