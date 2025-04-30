#include "position_collection.h"


void PositionCollection::open_positions(){
    for (size_t idx = 0; idx < this->trade_signal.size(); idx++){
        int signal_value = trade_signal[idx];
        double entry_price = this->market.close_prices[idx];

        PositionPtr position;

        if (signal_value == 1)
            position = std::make_unique<Long>(&market, entry_price, 1, 1, risk_managment.stop_loss_distance, risk_managment.take_profit_distance, idx);
        else
            position = std::make_unique<Short>(&market, entry_price, 1, 1, risk_managment.stop_loss_distance, risk_managment.take_profit_distance, idx);

        positions.push_back(std::move(position));
    }
}

void PositionCollection::close_positions(){
    for (const auto& position : this->positions){

        for (size_t time_idx = position->start_idx; time_idx < this->market.dates.size(); time_idx++){
            double market_price = market.close_prices[time_idx];
            if (position->stop_loss < market_price){
                position->check_exit_conditions(time_idx);
                break;
            }
        }
    }
}


void PositionCollection::display(){
    for (const PositionPtr& e : this->positions)
        e->display();
}
