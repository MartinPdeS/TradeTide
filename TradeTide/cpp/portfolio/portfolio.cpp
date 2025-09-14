// #define LOG_DEBUG(enabled, fmt, ...) \
//     do { if (enabled) { \
//         printf("[DEBUG][Portfolio - %-20s] " fmt "\n", __func__, ##__VA_ARGS__); \
//     } } while(0)
#define LOG_DEBUG(enabled, fmt, ...)                                     \
    do { if (enabled) {                                                  \
        int n = printf("[DEBUG][Portfolio - %s] ", __func__);            \
        if (n < 50) printf("%*s", 50 - n, "");                          \
        printf(fmt "\n", ##__VA_ARGS__);                                 \
    } } while(0)



#include "portfolio.h"

using Duration = std::chrono::system_clock::duration;
using TimePoint = std::chrono::system_clock::time_point;


// ---------------- Constructor ----------------
Portfolio::Portfolio(PositionCollection& position_collection, bool debug_mode): position_collection(position_collection), debug_mode(debug_mode) {
    this->record.state = &this->state;
    this->record.start_record(this->position_collection.market.dates.size());

    LOG_DEBUG(debug_mode, "Portfolio constructed\tMarketDates=%zu", position_collection.market.dates.size());
}



// ---------------- Public Methods ----------------
Metrics Portfolio::get_metrics() {
    Metrics metrics(this->record);
    metrics.calculate();
    return metrics;
}

void Portfolio::display() const {
    for (const auto& position : this->executed_positions) {
        position->display();
    }
}


// ---------------- Equity and Performance ----------------
double Portfolio::final_equity() const {
    return this->state.equity;
}

double Portfolio::peak_equity() const {
    return *std::max_element(this->record.equity.begin(), this->record.equity.end());
}


// ---------------- Position Management ----------------
void Portfolio::open_position(PositionPtr& position) {
    double lot_size = this->capital_management->can_open_position(position);

    if (lot_size == 0.0) {

        LOG_DEBUG(debug_mode,
            "[+]  Step: %-4zu/ %-4zu  Capital: %-7.2f  Equity: %-7.2f \tEntryPrice=%-7.2f \tLotSize=%.2f\tIdx=%zu\tType=%s",
            this->state.time_idx,
            this->state.n_elements,
            this->state.capital,
            this->state.equity,
            position->entry_price,
            position->lot_size,
            position->start_idx,
            position->is_long ? "Long" : "Short"
        );
        return;
    }

    position->lot_size = lot_size;
    this->active_positions.push_back(position);
    this->selected_positions.push_back(position);
    this->executed_positions.push_back(position);

    this->state.number_of_concurrent_positions += 1;
    this->state.capital -= position->entry_price * position->lot_size;
    position->is_closed = false;

    LOG_DEBUG(debug_mode,
        "[+]  Step: %-4zu/ %-4zu  Capital: %-7.2f  Equity: %-7.2f \tEntryPrice=%-7.2f \tLotSize=%.2f \tIdx=%zu \tType=%s",
        this->state.time_idx,
        this->state.n_elements,
        this->state.capital,
        this->state.equity,
        position->entry_price,
        position->lot_size,
        position->start_idx,
        position->is_long ? "Long" : "Short"
    );


}

void Portfolio::try_close_positions() {
    this->active_positions.erase(
        std::remove_if(
            this->active_positions.begin(),
            this->active_positions.end(),
            [&](PositionPtr& position) {
                if (position->close_idx == this->state.time_idx) {
                    // Close position before erasing it
                    this->state.number_of_concurrent_positions -= 1;
                    this->state.capital += position->exit_price * position->lot_size;
                    position->is_closed = true;
                    double profit_loss = position->get_price_difference();

                    if (profit_loss > 0)
                        ++this->record.success_count;
                    else if (profit_loss < 0)
                        ++this->record.fail_count;

                    this->executed_positions.push_back(position);

                    LOG_DEBUG(debug_mode,
                        "[-]  Step: %-4zu/%-4zu  Capital: %-7.2f  Equity: %-7.2f  "
                        "ExitPrice=%-7.2f  PnL=%-7.2f  LotSize=%-7.2f  IsLong=%s",
                        this->state.time_idx,
                        this->state.n_elements,
                        this->state.capital,
                        this->state.equity,
                        position->exit_price,
                        profit_loss,
                        position->lot_size,
                        position->is_long ? "True" : "False"
                    );

                    return true;  // remove this element
                }
                return false; // keep this element
            }),
        this->active_positions.end());
}


void Portfolio::try_open_positions() {
    while (this->state.position_index < this->position_collection.positions.size()) {

        // If we reached the end of positions, stop trying to open new ones
        if (this->position_collection.positions[this->state.position_index]->start_date != this->state.current_date)
            break;

        PositionPtr& position = this->position_collection.positions[this->state.position_index];

        // If we can't open more positions now, skip this one (but advance index!)
        this->open_position(position);

        ++this->state.position_index;
    }

}

void Portfolio::simulate(BaseCapitalManagement& capital_management) {
    this->selected_positions.clear();
    this->executed_positions.clear();
    this->active_positions.clear();

    this->capital_management = &capital_management;

    this->state = State(this->position_collection.market, this->capital_management->initial_capital);
    this->record.initial_capital = this->capital_management->initial_capital;
    this->capital_management->state  = &this->state;

    this->position_collection.set_all_position_to_open();

    for (size_t time_idx = 0; time_idx < this->position_collection.market.dates.size(); time_idx++) {
        this->state.update_time_idx(time_idx);

        this->try_close_positions();
        this->try_open_positions();

        this->state.capital_at_risk = this->calculate_capital_at_risk();
        this->state.equity = this->calculate_equity();
        this->record.update();

        LOG_DEBUG(debug_mode,
            "     Step: %-4zu/ %-4zu  Capital: %-7.2f  Equity: %-7.2f \tAtRisk=%-10.2f \tOpenPos=%-4zu",
            time_idx,
            this->state.n_elements,
            this->state.capital,
            this->state.equity,
            this->state.capital_at_risk,
            this->active_positions.size()
        );
    }

    if (!this->active_positions.empty()) {
        for (const auto& position : this->active_positions) {
            printf("position closed at %zu\n", position->close_idx);
        }
        throw std::runtime_error("There are still active positions after simulation!");
    }
}

void Portfolio::terminate_open_positions() {
    for (const auto& position : this->active_positions) {
        position->close_at(this->position_collection.market.dates.size() - 1);
        this->state.number_of_concurrent_positions -= 1;
        this->state.capital += position->exit_price * position->lot_size;
        this->executed_positions.push_back(position);

        LOG_DEBUG(debug_mode,
            "[-]  Step: %-4zu/ %-4zu  Capital: %-7.2f  Equity: %-7.2f \tExitPrice=%-8.2f \tLotSize=%-8.2f \tIndex=%-4zu  \tType=%-6s \7Exit index=%zu",
            this->state.time_idx,
            this->state.n_elements,
            this->state.capital,
            this->state.equity,
            position->exit_price,
            position->lot_size,
            position->start_idx,
            position->is_long ? "Long" : "Short",
            position->close_idx

        );

    }

    LOG_DEBUG(debug_mode, "All remaining positions terminated\tCount=%zu", this->active_positions.size());

    this->active_positions.clear();
}

const std::vector<TimePoint>& Portfolio::get_market_dates() const {
    return this->position_collection.get_market().dates;
}

std::vector<BasePosition*> Portfolio::get_positions(size_t count) const {
    if (count == std::numeric_limits<size_t>::max())
        count = this->selected_positions.size();

    std::vector<BasePosition*> result;
    result.reserve(std::min(count, this->selected_positions.size()));

    for (const auto& up : this->selected_positions) {
        result.push_back(up.get());
        if (result.size() >= count)
            break;
    }

    return result;
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
        equity += position->exit_price * position->lot_size;


    return equity;
}
