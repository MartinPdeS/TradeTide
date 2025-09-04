#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "position_collection.h"


namespace py = pybind11;

PYBIND11_MODULE(interface_position_collection, module) {
    module.doc() = R"pbdoc(
        Python bindings for the PositionCollection class.

        PositionCollection manages a group of trading positions (Long or Short) over time,
        based on a signal and a market. It applies a defined ExitStrategy to each position,
        handles trade execution and tracking, and provides utilities to extract trading data
        such as entry/exit prices, dates, and SL/TP levels.
    )pbdoc";


    // Bind the Position class
    py::class_<PositionCollection, std::shared_ptr<PositionCollection>>(module, "POSITIONCOLLECTION")
        .def(
            py::init<const Market&, const std::vector<int>&, const bool&, const bool&>(),
            py::arg("market"),
            py::arg("trade_signal"),
            py::arg("save_price_data") = false,
            py::arg("debug_mode") = false,
            R"pbdoc(
                Create a new PositionCollection.

                Args:
                    market (Market): Reference to the Market object used for price and time series.
                    risk_managment (ExitStrategy): Exit strategy template applied to each position.
                    signal (Signal): Signal array with trade entry instructions (1=long, -1=short, 0=ignore).
                    save_price_data (bool): Whether to record SL/TP price history over time.
            )pbdoc"
        )
        .def_readwrite("debug_mode", &PositionCollection::debug_mode,
            R"pbdoc(
                Enable or disable debug output for development purposes.
            )pbdoc"
        )
        .def("open_positions", &PositionCollection::open_positions,
            py::arg("exit_strategy"),
            R"pbdoc(
                Initialize all trading positions according to the signal.

                This uses the `signal` provided during construction to instantiate Long or Short
                positions at the appropriate time indices. Each position gets a cloned ExitStrategy.
            )pbdoc")

        .def("propagate_positions", &PositionCollection::propagate_positions,
            R"pbdoc(
                Close all positions based on their exit strategy rules.

                This method propagates market data through each position's strategy and
                closes them at either stop-loss or take-profit, whichever is hit first.
            )pbdoc")

        .def("terminate_open_positions", &PositionCollection::terminate_open_positions,
            R"pbdoc(
                Force-close any remaining open positions at the last available market price.
            )pbdoc")

        .def("display", &PositionCollection::display,
            R"pbdoc(
                Print summary information about all positions in the collection.
            )pbdoc")

        .def("__getitem__", &PositionCollection::__getitem__, py::return_value_policy::reference_internal) // keep parent alive

        .def("__len__", &PositionCollection::size,
            R"pbdoc(
                Get the number of positions in the collection.
            )pbdoc")

        .def("get_start_dates", &PositionCollection::get_start_dates,
            R"pbdoc(
                Return a list of position start dates.
            )pbdoc")

        .def("get_close_dates", &PositionCollection::get_close_dates,
            R"pbdoc(
                Return a list of position close dates.
            )pbdoc")

        .def("get_entry_prices", &PositionCollection::get_entry_prices,
            R"pbdoc(
                Return a list of entry prices for all positions.
            )pbdoc")

        .def("get_exit_prices", &PositionCollection::get_exit_prices,
            R"pbdoc(
                Return a list of exit prices for all positions.
            )pbdoc")

        .def_readwrite("number_of_trade", &PositionCollection::number_of_trade,
            R"pbdoc(
                The number of trades (non-zero entries in the signal).
            )pbdoc")

        .def("get_market", &PositionCollection::get_market,
            R"pbdoc(
                Get a reference to the underlying Market object used in the collection.
            )pbdoc")

        .def_readonly("save_price_data", &PositionCollection::save_price_data,
            R"pbdoc(
                Whether SL/TP data was saved for each position over time.
            )pbdoc")

        .def("to_csv", &PositionCollection::to_csv,
            py::arg("filepath"),
            R"pbdoc(
                Export the position collection to a CSV file.

                Args:
                    filepath (str): Path to the output CSV file.
            )pbdoc")
        ;
}
