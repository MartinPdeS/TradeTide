#include "position.h"

#include "../exit_strategy/exit_strategy.h"


// Base Position---------------------------------------------

BasePosition::BasePosition(const ExitStrategy &exit_strategy, size_t start_idx, bool is_long)
: start_idx(start_idx), is_long(is_long), is_closed(false)
{
    this->exit_strategy = exit_strategy.clone();
}

// The logic here is as follows:
// Position open price is set to ask/bid close price depending on whether the position is long or short.
void BasePosition::initialize_state(const size_t time_idx) {

    this->state.update_time_idx(time_idx);
    this->start_date = this->state.current_date;
    this->entry_price = this->state.opening_price->close;
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

void BasePosition::terminate_with_stop_lose(const size_t time_idx) {

    // If stop-loss is hit, close the position at the stop-loss price
    this->exit_price = this->exit_strategy->stop_loss_price;
    this->close_date = this->state.current_date;
    this->close_idx = time_idx;
    this->is_closed = true;
}

void BasePosition::terminate_with_take_profit(const size_t time_idx) {
    this->exit_price = this->exit_strategy->take_profit_price;
    this->close_date = this->state.current_date;
    this->close_idx = time_idx;
    this->is_closed = true;
}

double BasePosition::get_capital_at_risk() const {
    return std::abs(this->entry_price - this->exit_strategy->stop_loss_price) * this->lot_size;
}

void BasePosition::close_at(const size_t time_idx) {
    this->exit_price = (*this->state.closing_prices)[time_idx];
    this->close_date = (*this->state.dates)[time_idx];
    this->close_idx = time_idx;
    this->is_closed = true;
}


// Display Position Info
void BasePosition::display() const {
    if (this->is_long)
        std::cout << "Long Position:\n";
    else
        std::cout << "Short Position:\n";

    std::cout << std::fixed << std::setprecision(5)
        << "Start Time: " << start_date << "\n"
        << "Stop Time: " << close_date << "\n"
        << "Entry Price: " << entry_price << "\n"
        << "Exit Price: " << exit_price << "\n"
        << "Lot Size: " << lot_size << "\n\n"
    ;
}

double BasePosition::get_closing_value_at(const size_t time_idx) const {
    return (*this->state.closing_prices)[time_idx] * this->lot_size;
}


// Check if stop-loss or take-profit is hit
void BasePosition::propagate() {
    for (size_t time_idx = this->start_idx; time_idx < this->state.n_elements; time_idx++) {
        this->state.update_time_idx(time_idx);

        this->exit_strategy->update_price();

        if (this->is_stop_loss_triggered())  // Hit stop-loss
            return this->terminate_with_stop_lose(time_idx);

        if (this->is_take_profit_triggered())  // Hit take-profit
            return this->terminate_with_take_profit(time_idx);
    }
}

// --------------------- Long Position ------------------------
Long::Long(const ExitStrategy &exit_strategy, const size_t time_idx, const Market &market)
    : BasePosition(exit_strategy, time_idx, true)
{
    this->state = State(market);
    this->state.opening_price = &this->state.ask;
    this->state.closing_price = &this->state.bid;
    this->state.closing_prices = &this->state.market->bid.open;
    this->initialize_state(time_idx);
}

[[nodiscard]] double Long::get_price_difference() const {
    return this->exit_price - this->entry_price;
}

bool Long::is_stop_loss_triggered() const {
    return this->state.closing_price->low <= this->exit_strategy->stop_loss_price;
}

bool Long::is_take_profit_triggered() const {
    return this->state.closing_price->high >= this->exit_strategy->take_profit_price;
}


// --------------------- Short Position ------------------------
Short::Short(const ExitStrategy &exit_strategy, const size_t time_idx, const Market &market)
    : BasePosition(exit_strategy, time_idx, false)
{
    this->state = State(market);
    this->state.opening_price = &this->state.bid;
    this->state.closing_price = &this->state.ask;
    this->state.closing_prices = &this->state.market->ask.open;
    this->initialize_state(time_idx);
}


bool Short::is_stop_loss_triggered() const {
    return this->state.closing_price->high >= this->exit_strategy->stop_loss_price;
}

bool Short::is_take_profit_triggered() const {
    return this->state.closing_price->low <= this->exit_strategy->take_profit_price;
}

// Calculate profit or loss
[[nodiscard]] double Short::get_price_difference() const {
    return this->entry_price - this->exit_price;
}
