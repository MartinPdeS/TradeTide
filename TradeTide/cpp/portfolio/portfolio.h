#pragma once

#include <memory>
#include <vector>

#include "../position_collection/position_collection.h"
#include "../capital_management/capital_management.h"

class Portfolio {
    public:
        PositionCollection& position_collection;
        BaseCapitalManagement& capital_management;

        Portfolio(PositionCollection& position_collection, BaseCapitalManagement& capital_management)
        :
            position_collection(position_collection),
            capital_management(capital_management)
            {};

        void simulate();

        std::vector<double> equity_history;
        std::vector<size_t> open_position_count;

        [[nodiscard]] double final_equity() const;
        [[nodiscard]] double peak_equity() const;
        [[nodiscard]] std::vector<double> equity_curve() const;

        void display() const;
        void compute_open_position_count_over_time();
        void compute_equity_over_time();
        [[nodiscard]] const std::vector<TimePoint>& get_market_dates() const;
        [[nodiscard]] std::vector<double> equity_over_time() const;
        [[nodiscard]] const Market& get_market(){return this->position_collection.market;}
        [[nodiscard]] const std::vector<PositionPtr>& get_positions(){return this->selected_positions;}

    private:
        std::vector<PositionPtr> selected_positions; // <- filled from position_collection.positions
        std::vector<PositionPtr> active_positions;
        std::vector<PositionPtr> executed_positions;

        void reset_state();
        void finalize_closed_positions();
        void activate_positions_at(const TimePoint& current_time, const std::vector<PositionPtr>& all_positions, size_t& position_index);
        void finalize_remaining_open_positions();



    };
