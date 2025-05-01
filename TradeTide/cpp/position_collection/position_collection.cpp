#include "position_collection.h"


void PositionCollection::open_positions(){

    for (size_t idx = 0; idx < number_of_trade; idx++){
        int signal_value = signal.trade_signal[idx];
        double entry_price = this->market.close_prices[idx];

        PositionPtr position;

        position = std::make_unique<Long>(market, risk_managment, 1, 1, 1, idx);

        if (signal_value == 1)
            position = std::make_unique<Long>(market, risk_managment, entry_price, 1, 1, idx);
        else
            position = std::make_unique<Short>(market, risk_managment, entry_price, 1, 1, idx);

        this->risk_managment.update_position_lot_size(*position, 10);
        positions.push_back(std::move(position));
    }
}

void PositionCollection::close_positions(){
    for (const auto& position : this->positions){

        for (size_t time_idx = position->start_idx; time_idx < this->market.dates.size(); time_idx++){
            position->check_exit_conditions(time_idx);

            if (position->is_closed)
                break;
        }
    }
}


void PositionCollection::display(){
    for (const PositionPtr& e : this->positions)
        e->display();
}
