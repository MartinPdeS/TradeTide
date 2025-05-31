#include "position.h"

#include "../exit_strategy/exit_strategy.h"


// Base Position---------------------------------------------

BasePosition::BasePosition(const ExitStrategy &exit_strategy, size_t start_idx, bool is_long)
: start_idx(start_idx), is_long(is_long), is_closed(false)
{
    this->exit_strategy = exit_strategy.clone();
}

void BasePosition::initialize_state(const Market& market, const size_t time_idx) {

    this->state.update_time_idx(time_idx);
    this->start_date = this->state.time;
    this->entry_price = this->state.open_price->open;
    this->exit_strategy->position = this;
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
    this->close_date = this->state.time;
    this->close_idx = time_idx;
    this->is_terminated = true;
}

double BasePosition::get_capital_at_risk() const {
    return std::abs(this->entry_price - this->exit_strategy->stop_loss_price) * this->lot_size;
}

// Long Position---------------------------------------------
Long::Long(const ExitStrategy &exit_strategy, const size_t time_idx, const Market &market)
    : BasePosition(exit_strategy, time_idx, true)
{
    this->state = State(market);
    this->state.open_price = &this->state.ask;
    this->state.close_price = &this->state.bid;
    this->initialize_state(market, time_idx);
}

// Check if stop-loss or take-profit is hit
void Long::propagate() {
    for (size_t time_idx = this->start_idx; time_idx < this->state.n_elements; time_idx++) {
        this->state.update_time_idx(time_idx);

        this->exit_strategy->update_price();

        if (this->state.close_price->low <= this->exit_strategy->stop_loss_price) // Hit stop-loss
            return this->terminate(this->exit_strategy->stop_loss_price, time_idx);

        if (this->state.close_price->high >= this->exit_strategy->take_profit_price)   // Hit take-profit
            return this->terminate(this->exit_strategy->take_profit_price, time_idx);

    }
}

double Long::get_closing_value_at(const size_t time_idx) const {
    return this->state.market->bid.open[time_idx] * this->lot_size;
}

void Long::set_close_condition(const size_t time_idx) {
    this->exit_price = this->state.close_price->open;
    this->close_date = this->state.close_price->date;
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
Short::Short(const ExitStrategy &exit_strategy, const size_t time_idx, const Market &market)
    : BasePosition(exit_strategy, time_idx, false)
{
    this->state = State(market);
    this->state.open_price = &this->state.bid;
    this->state.close_price = &this->state.ask;
    this->initialize_state(market, time_idx);
}

// Check if stop-loss or take-profit is hit
void Short::propagate() {
    for (size_t time_idx = this->start_idx; time_idx < this->state.n_elements; time_idx++) {
        this->state.update_time_idx(time_idx);

        this->exit_strategy->update_price();

        if (this->state.close_price->high >= this->exit_strategy->stop_loss_price)  // Hit stop-loss
            return this->terminate(this->exit_strategy->stop_loss_price, time_idx);
            this->exit_price = this->exit_strategy->stop_loss_price;

        if (this->state.close_price->low <= this->exit_strategy->take_profit_price)  // Hit take-profit
            return this->terminate(this->exit_strategy->take_profit_price, time_idx);
    }
}

void Short::set_close_condition(const size_t time_idx) {
    this->exit_price = this->state.close_price->open;
    this->close_date = this->state.time;
}

double Short::get_closing_value_at(const size_t time_idx) const {
    return this->state.market->ask.open[time_idx] * this->lot_size;
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
