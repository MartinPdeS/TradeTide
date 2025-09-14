#define LOG_DEBUG(enabled, fmt, ...) \
    do { if (enabled) { \
        printf("[DEBUG][PositionCollection - %s] " fmt "\n", __func__, ##__VA_ARGS__); \
    } } while(0)


#include "position_collection.h"

PositionCollection::PositionCollection(const Market& market, const std::vector<int>& trade_signal, const bool save_price_data, const bool debug_mode)
    : market(market), trade_signal(trade_signal), save_price_data(save_price_data), debug_mode(debug_mode)
{
    this->number_of_trade = std::count_if(
        this->trade_signal.begin(),
        this->trade_signal.end(),
        [](int x) { return x != 0; }
    );

    this->positions.reserve(this->number_of_trade);

    LOG_DEBUG(this->debug_mode, "PositionCollection initialized with %zu trades to process\n", this->number_of_trade);

}

std::vector<double> PositionCollection::extract_vector(std::function<double(PositionPtr)> accessor) {
    std::vector<double> array;
    array.reserve(this->positions.size());

    for (const PositionPtr& position : this->positions)
        array.push_back(accessor(position));

    return array;
}

std::vector<TimePoint> PositionCollection::extract_vector(std::function<TimePoint(PositionPtr)> accessor) {
    std::vector<TimePoint> array;
    array.reserve(this->positions.size());

    for (const PositionPtr& position : this->positions)
        array.push_back(accessor(position));

    return array;
}

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

        LOG_DEBUG(debug_mode,
            "Opened position  Type=%-5s  TimeIdx=%-6zu  StartIdx=%-6zu",
            signal_value == 1 ? "Long" : "Short",
            time_idx,
            position->start_idx);
                positions.push_back(std::move(position));
            }

        LOG_DEBUG(debug_mode, "Total positions opened  Count=%-6zu\n", positions.size());
}



void PositionCollection::propagate_positions() {
    LOG_DEBUG(debug_mode, "Propagating %zu positions...", positions.size());

    #pragma omp parallel for
    for (const auto& position : positions) {
        position->propagate();
        LOG_DEBUG(debug_mode,
            "Propagated position #%-4zu  [%-5s]  entry: %-8.2f  lot: %-6.2f  is_closed: %s",
            position->start_idx,
            position->is_long ? "Long" : "Short",
            position->entry_price,
            position->lot_size,
            position->is_closed ? "True" : "False"
        );
    }

    LOG_DEBUG(debug_mode, "All positions propagated\n");

    this->terminate_open_positions();

    for (auto& position : this->positions)
        printf(
            "Position #%-4zu  [%-5s]  entry: %-8.2f  exit: %-8.2f  lot: %-6.2f  pnl: %-8.2f  is_closed: %s\n",
            position->start_idx,
            position->is_long ? "Long" : "Short",
            position->entry_price,
            position->exit_price,
            position->lot_size,
            position->get_price_difference(),
            position->is_closed ? "True" : "False"
        );

    std::sort(
        this->positions.begin(),
        this->positions.end(),
        [](const PositionPtr& a, const PositionPtr& b) { return a->start_date < b->start_date; }
    );

    #pragma omp parallel for
    for (PositionPtr& position : this->positions)
        if (position->close_date == position->start_date) {
            position->display();
            throw std::runtime_error("Position cannot be closed at the same time it is opened!");
        }
}


void PositionCollection::terminate_open_positions() {
    for (const auto& position : this->positions) {
        if (!position->is_closed) {
            position->close_at(this->market.dates.size() - 1);
            position->is_closed = true;

        LOG_DEBUG(debug_mode,
            "Terminated unclosed position %s \tstart_idx: %zu \texit_price: %.2f \tlot_size: %.2f \tpnl: %.2f",
            position->is_long ? "[Long]" : "[Short]",
            position->start_idx,
            position->exit_price,
            position->lot_size,
            position->get_price_difference()
        );
        }
    }

    LOG_DEBUG(debug_mode, "Checked all positions for termination\n");
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

[[nodiscard]] std::vector<TimePoint> PositionCollection::get_start_dates() {
    return this->extract_vector(
        [](const PositionPtr& p) { return p->start_date; });
}

[[nodiscard]] std::vector<TimePoint> PositionCollection::get_close_dates() {
    return this->extract_vector(
        [](const PositionPtr& p) { return p->close_date; });
}

[[nodiscard]] std::vector<double> PositionCollection::get_entry_prices() {
    return this->extract_vector(
        [](const PositionPtr& p) { return p->entry_price; });
}

[[nodiscard]] std::vector<double> PositionCollection::get_exit_prices() {
    return this->extract_vector(
        [](const PositionPtr& p) { return p->exit_price; });
}

void PositionCollection::set_position_to_close() {
    for (auto& position : this->positions) {
        position->is_closed = true;
    }
}

void PositionCollection::set_all_position_to_open() {
    for (auto& position : this->positions) {
        position->is_closed = false;
    }
}
