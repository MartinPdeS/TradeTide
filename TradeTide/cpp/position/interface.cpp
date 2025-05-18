#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "position.h"
#include "../exit_strategy/exit_strategy.h"

namespace py = pybind11;

PYBIND11_MODULE(interface_position, module) {
    module.doc() = "Python bindings for trading positions (BasePosition, Long, Short) and their properties.";

    py::class_<BasePosition>(module, "BasePosition")
        .def_readwrite("entry_price", &BasePosition::entry_price,
            R"pbdoc(
                Entry price of the position.

                This is the market price at which the position was opened.
            )pbdoc")
        .def_readwrite("lot_size", &BasePosition::lot_size,
            R"pbdoc(
                Lot size of the position.

                Defines the size of the position in trading lots (e.g. 1.0 = standard lot).
            )pbdoc")
        .def_readwrite("start_date", &BasePosition::start_date,
            R"pbdoc(
                Datetime when the position was opened.
            )pbdoc")
        .def_readwrite("close_date", &BasePosition::close_date,
            R"pbdoc(
                Datetime when the position was closed.
            )pbdoc")
        .def("display", &BasePosition::display,
            R"pbdoc(
                Print a summary of the position details to the console.
            )pbdoc")
        .def("calculate_profite_and_loss", &BasePosition::calculate_profite_and_loss,
            R"pbdoc(
                Calculate the total profit or loss of the position.

                Returns:
                    float: Profit (positive) or loss (negative).
            )pbdoc")
        .def_readonly("is_closed", &BasePosition::is_closed,
            R"pbdoc(
                Whether the position has been closed.
            )pbdoc")
        .def("stop_loss_prices", &BasePosition::strategy_stop_loss_prices,
            R"pbdoc(
                List of stop-loss price values over time.

                These are updated according to the ExitStrategy applied to the position.
            )pbdoc")
        .def("take_profit_prices", &BasePosition::strategy_take_profit_prices,
            R"pbdoc(
                List of take-profit price values over time.

                These are updated according to the ExitStrategy applied to the position.
            )pbdoc")
        .def("dates", &BasePosition::strategy_dates,
            R"pbdoc(
                List of timestamps corresponding to each SL/TP update.

                Used for aligning SL/TP data to the market time series.
            )pbdoc")
        .doc() = R"pbdoc(
            Abstract base class for a trading position.

            This class defines the common structure and behavior of both long and short positions.
            It includes entry/exit pricing, position size, timestamps, and strategy linkage.
        )pbdoc";

    py::class_<Long, BasePosition>(module, "Long",
        R"pbdoc(
            Long trading position (buy low, sell high).

            This subclass of BasePosition represents a position that profits when the market price increases.
        )pbdoc");

    py::class_<Short, BasePosition>(module, "Short",
        R"pbdoc(
            Short trading position (sell high, buy low).

            This subclass of BasePosition represents a position that profits when the market price decreases.
        )pbdoc");
}
