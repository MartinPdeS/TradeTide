#include "exit_strategy.h"

#include "../position/position.h"



// --------------------------- ExitStrategy --------------------------------------

void ExitStrategy::initialize_prices() {
    if (this->position->is_long)
        this->stop_loss_price = this->position->state.bid.open - this->stop_loss_pip * this->position->state.market->pip_value;
    else
        this->stop_loss_price = this->position->state.ask.open + this->stop_loss_pip * this->position->state.market->pip_value;
}


void ExitStrategy::update_price() {
    this->update_stop_loss_price();
    this->update_take_profit_price();

    if (this->save_price_data) {
        this->dates.push_back(this->position->state.ask.date);
        this->stop_loss_prices.push_back(this->stop_loss_price);
        this->take_profit_prices.push_back(this->take_profit_price);
    }
}


// --------------------------- StaticExitStrategy --------------------------------------
std::unique_ptr<ExitStrategy> StaticExitStrategy::clone() const {
    return std::make_unique<StaticExitStrategy>(*this);
}

void StaticExitStrategy::update_stop_loss_price() {}

void StaticExitStrategy::update_take_profit_price() {}



// --------------------------- TrailingExitStrategy --------------------------------------
std::unique_ptr<ExitStrategy> TrailingExitStrategy::clone() const {
    return std::make_unique<TrailingExitStrategy>(*this);
}

void TrailingExitStrategy::update_stop_loss_price() {
    double new_price;

    new_price = this->position->state.bid.low + this->take_profit_pip * this->position->state.market->pip_value;
    if (this->position->is_long && new_price > this->stop_loss_price) {
        this->stop_loss_price = new_price;
        return;
    }

    new_price = this->position->state.ask.low - this->take_profit_pip * this->position->state.market->pip_value;
    if (!this->position->is_long && new_price < this->stop_loss_price) {
        this->stop_loss_price = new_price;
        return;
    }

}

void TrailingExitStrategy::update_take_profit_price() {
    double new_price;

    new_price = this->position->state.bid.high + this->take_profit_pip * this->position->state.market->pip_value;
    if (this->position->is_long && new_price < this->take_profit_price) {
        this->take_profit_price = new_price;
        return;
    }

    new_price = this->position->state.ask.low - this->take_profit_pip * this->position->state.market->pip_value;
    if (!this->position->is_long && new_price > this->take_profit_price) {
        this->take_profit_price = new_price;
        return;
    }
}



// --------------------------- BreakEvenExitStrategy --------------------------------------
std::unique_ptr<ExitStrategy> BreakEvenExitStrategy::clone() const {
    return std::make_unique<BreakEvenExitStrategy>(*this);
}

void BreakEvenExitStrategy::update_stop_loss_price() {
    if (!break_even_triggered) {
        double distance_moved;

        if (this->position->is_long) { // Normal SL until break-even level is hit
            stop_loss_price = this->position->entry_price - stop_loss_pip * this->position->state.market->pip_value;
            distance_moved = std::abs(this->position->state.bid.open - this->position->entry_price) / this->position->state.market->pip_value;

        }
        else {
            stop_loss_price = this->position->entry_price + stop_loss_pip * this->position->state.market->pip_value;
            distance_moved = std::abs(this->position->state.ask.open - this->position->entry_price) / this->position->state.market->pip_value;

        }
        if (distance_moved >= break_even_trigger_pip) {
            stop_loss_price = this->position->entry_price;
            break_even_triggered = true;
        }
    }
}

void BreakEvenExitStrategy::update_take_profit_price() {
    if (this->position->is_long)
        take_profit_price = this->position->entry_price + take_profit_pip * this->position->state.market->pip_value;
    else
        take_profit_price = this->position->entry_price - take_profit_pip * this->position->state.market->pip_value;
}



