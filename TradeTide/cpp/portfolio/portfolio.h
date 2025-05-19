#pragma once

#include <memory>
#include <vector>

#include "../position_collection/position_collection.h"

class Portfolio {
    public:
        Portfolio(PositionCollection& position_collection, double initial_capital, size_t max_concurrent_positions, double max_lot_size, double max_capital_at_risk)
        : position_collection(position_collection),
          initial_capital(initial_capital),
          equity(initial_capital),
          max_lot_size(max_lot_size),
          max_capital_at_risk(max_capital_at_risk),
          max_concurrent_positions(max_concurrent_positions) {};

        void simulate();

        [[nodiscard]] double final_equity() const;
        [[nodiscard]] double peak_equity() const;
        [[nodiscard]] std::vector<double> equity_curve() const;

        void display() const;
        [[nodiscard]] std::vector<size_t> open_position_count_over_time() const;
        [[nodiscard]] const std::vector<TimePoint>& get_market_dates() const;
        [[nodiscard]] std::vector<double> equity_over_time() const;

    private:
        PositionCollection& position_collection;

        double initial_capital;
        double equity;
        double max_lot_size;
        double max_capital_at_risk;
        size_t max_concurrent_positions;

        std::vector<PositionPtr> active_positions;
        std::vector<PositionPtr> executed_positions;
        std::vector<double> equity_history;


    };
