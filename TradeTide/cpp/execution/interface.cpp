#include <pybind11/chrono.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <chrono>
#include <stdexcept>
#include <utility>
#include <vector>

#include "position/position.h"

namespace py = pybind11;

struct TradeCost {
    double commission = 0.0;
    double slippage = 0.0;
    double spread = 0.0;
    double financing = 0.0;

    [[nodiscard]] double total() const {
        return commission + slippage + spread + financing;
    }
};

struct ExecutionCosts {
    double commission_per_lot = 0.0;
    double slippage_pips = 0.0;
    double extra_spread_pips = 0.0;
    double financing_per_lot_per_night = 0.0;

    ExecutionCosts(
        double commission = 0.0,
        double slippage = 0.0,
        double extra_spread = 0.0,
        double financing = 0.0
    )
        : commission_per_lot(commission),
          slippage_pips(slippage),
          extra_spread_pips(extra_spread),
          financing_per_lot_per_night(financing) {
        if (commission < 0.0 || slippage < 0.0 || extra_spread < 0.0 || financing < 0.0) {
            throw std::invalid_argument("Execution costs must be non-negative.");
        }
    }

    [[nodiscard]] static long nights(const BasePosition& position) {
        const auto duration = position.close_date - position.start_date;
        return std::max(0L, std::chrono::duration_cast<std::chrono::hours>(duration).count() / 24);
    }

    [[nodiscard]] TradeCost for_trade(const BasePosition& position, double pip_value) const {
        const double lot_size = position.lot_size;
        return {
            2.0 * commission_per_lot * lot_size,
            2.0 * slippage_pips * pip_value * lot_size,
            extra_spread_pips * pip_value * lot_size,
            static_cast<double>(nights(position)) * financing_per_lot_per_night * lot_size,
        };
    }

    [[nodiscard]] std::vector<std::pair<TimePoint, double>> cashflow_events(
        const BasePosition& position, const TradeCost& trade_cost
    ) const {
        const double entry_cost = (trade_cost.commission + trade_cost.slippage + trade_cost.spread) / 2.0;
        std::vector<std::pair<TimePoint, double>> events{{position.start_date, entry_cost}};
        for (long night = 1; night <= nights(position); ++night) {
            events.emplace_back(
                position.start_date + std::chrono::hours(24 * night),
                financing_per_lot_per_night * position.lot_size
            );
        }
        events.emplace_back(position.close_date, entry_cost);
        return events;
    }
};

PYBIND11_MODULE(execution, module) {
    module.doc() = "Native execution-cost models for completed trades.";

    py::class_<TradeCost>(module, "TradeCost")
        .def(py::init<double, double, double, double>(),
            py::arg("commission") = 0.0,
            py::arg("slippage") = 0.0,
            py::arg("spread") = 0.0,
            py::arg("financing") = 0.0)
        .def_readonly("commission", &TradeCost::commission)
        .def_readonly("slippage", &TradeCost::slippage)
        .def_readonly("spread", &TradeCost::spread)
        .def_readonly("financing", &TradeCost::financing)
        .def_property_readonly("total", &TradeCost::total);

    py::class_<ExecutionCosts>(module, "ExecutionCosts")
        .def(py::init<double, double, double, double>(),
            py::arg("commission_per_lot") = 0.0,
            py::arg("slippage_pips") = 0.0,
            py::arg("extra_spread_pips") = 0.0,
            py::arg("financing_per_lot_per_night") = 0.0)
        .def_readonly("commission_per_lot", &ExecutionCosts::commission_per_lot)
        .def_readonly("slippage_pips", &ExecutionCosts::slippage_pips)
        .def_readonly("extra_spread_pips", &ExecutionCosts::extra_spread_pips)
        .def_readonly("financing_per_lot_per_night", &ExecutionCosts::financing_per_lot_per_night)
        .def("for_trade", [](const ExecutionCosts& self, const py::object& position, double pip_value) {
            const double lot_size = py::cast<double>(position.attr("lot_size"));
            const auto duration = position.attr("close_date") - position.attr("start_date");
            const long overnight_periods = std::max(0L, py::cast<long>(duration.attr("days")));
            return TradeCost{
                2.0 * self.commission_per_lot * lot_size,
                2.0 * self.slippage_pips * pip_value * lot_size,
                self.extra_spread_pips * pip_value * lot_size,
                static_cast<double>(overnight_periods) * self.financing_per_lot_per_night * lot_size,
            };
        }, py::arg("position"), py::arg("pip_value"))
        .def("cashflow_events", [](const ExecutionCosts& self, const py::object& position, const TradeCost& trade_cost) {
            const py::object start = position.attr("start_date");
            const py::object close = position.attr("close_date");
            const double lot_size = py::cast<double>(position.attr("lot_size"));
            const auto duration = close - start;
            const long overnight_periods = std::max(0L, py::cast<long>(duration.attr("days")));
            const double entry_cost = (trade_cost.commission + trade_cost.slippage + trade_cost.spread) / 2.0;
            const py::object timedelta = py::module_::import("datetime").attr("timedelta");
            py::list events;
            events.append(py::make_tuple(start, entry_cost));
            for (long night = 1; night <= overnight_periods; ++night) {
                events.append(py::make_tuple(
                    start + timedelta(py::arg("days") = night),
                    self.financing_per_lot_per_night * lot_size
                ));
            }
            events.append(py::make_tuple(close, entry_cost));
            return events;
        }, py::arg("position"), py::arg("trade_cost"));
}
