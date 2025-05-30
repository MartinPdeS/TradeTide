#include "position.h"

#include "../exit_strategy/exit_strategy.h"
#include "../state/state.h"


// Base Position---------------------------------------------

BasePosition::BasePosition(std::unique_ptr<ExitStrategy> exit_strategy, double entry_price, TimePoint start_date, size_t open_idx, bool is_long)
: exit_strategy(std::move(exit_strategy)), entry_price(entry_price), start_date(start_date), open_idx(open_idx), is_long(is_long), is_closed(false)
{
    this->exit_strategy->initialize_prices();
}

const std::vector<double>& BasePosition::strategy_stop_loss_prices() const {
    return this->exit_strategy->stop_loss_prices;
}

const std::vector<double>& BasePosition::strategy_take_profit_prices() const {
    return this->exit_strategy->take_profit_prices;
}

const std::vector<TimePoint>& BasePosition::strategy_dates() const {
    return this->exit_strategy->dates;
}

void BasePosition::terminate(const double exit_price, const size_t time_idx) {
    this->exit_price = exit_price;
    this->close_date = this->prices->dates[time_idx];
    this->close_idx = time_idx;
    this->is_terminated = true;
}

double BasePosition::get_capital_at_risk() const {
    return std::abs(this->entry_price - this->exit_strategy->stop_loss_price) * this->lot_size;
}

// Long Position---------------------------------------------
// Check if stop-loss or take-profit is hit
void Long::propagate() {
    for (size_t time_idx = this->open_idx; time_idx < this->prices->dates.size(); time_idx++) {
        this->exit_strategy->update_price();

        if (this->prices->low[time_idx] <= this->exit_strategy->stop_loss_price) // Hit stop-loss
            return this->terminate(this->exit_strategy->stop_loss_price, time_idx);

        if (this->prices->high[time_idx] >= this->exit_strategy->take_profit_price)   // Hit take-profit
            return this->terminate(this->exit_strategy->take_profit_price, time_idx);

    }
}

double Long::get_closing_value_at(const size_t time_idx) const {
    return  this->prices->open[time_idx] * this->lot_size;
}

void Long::set_close_condition(const size_t time_idx) {
    this->exit_price = this->prices->open[time_idx];
    this->close_date = this->prices->dates[time_idx];
}

// Calculate profit or loss
[[nodiscard]] double Long::get_price_difference() const {
    return this->exit_price - this->entry_price;
}

// Display Position Info
void Long::display() const {
    std::cout
        << "Position Type: Long \n"
        << "Start Time: " << start_date << "\n"
        << "Stop Time: " << close_date << "\n"
        << "Entry Price: " << entry_price << "\n"
        << "Exit Price: " << exit_price << "\n"
        << "Lot Size: " << lot_size << "\n\n"
    ;
}


// Short Position---------------------------------------------
void Short::propagate() {
    for (size_t time_idx = this->open_idx; time_idx < this->prices->dates.size(); time_idx++) {

        this->state.time_idx = time_idx;

        this->exit_strategy->update_price();

        if (this->prices->high[time_idx] >= this->exit_strategy->stop_loss_price)  // Hit stop-loss
            return this->terminate(this->exit_strategy->stop_loss_price, time_idx);
            this->exit_price = this->exit_strategy->stop_loss_price;

        if (this->prices->low[time_idx] <= this->exit_strategy->take_profit_price)  // Hit take-profit
            return this->terminate(this->exit_strategy->take_profit_price, time_idx);
    }
}

void Short::set_close_condition(const size_t time_idx) {
    this->exit_price = this->prices->open[time_idx];
    this->close_date = this->prices->dates[time_idx];
}

double Short::get_closing_value_at(const size_t time_idx) const {
    return  this->prices->open[time_idx] * this->lot_size;
}

// Calculate profit or loss
[[nodiscard]] double Short::get_price_difference() const {
    return this->entry_price - this->exit_price;
}


// Display Position Info
void Short::display() const {
    std::cout
        << "Position Type: Short\n"
        << "Start Time: " << start_date << "\n"
        << "Stop Time: " << close_date << "\n"
        << "Entry Price: " << entry_price << "\n"
        << "Exit Price: " << exit_price<< "\n"
        << "Lot Size: " << lot_size << "\n\n"
    ;
}
