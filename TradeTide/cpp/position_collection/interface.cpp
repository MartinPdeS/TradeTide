#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include <limits>
#include "position_collection.h"


namespace py = pybind11;

PYBIND11_MODULE(position_collection, module) {
    module.doc() = R"pbdoc(
        Python bindings for the PositionCollection class.

        PositionCollection manages a group of trading positions (Long or Short) over time,
        based on a signal and a market. It applies a defined ExitStrategy to each position,
        handles trade execution and tracking, and provides utilities to extract trading data
        such as entry/exit prices, dates, and SL/TP levels.
    )pbdoc";


    // Bind the Position class
    py::class_<PositionCollection, std::shared_ptr<PositionCollection>>(module, "PositionCollection", R"pbdoc(
        Candidate positions generated from a market-aligned trade-signal vector.

        Positions are constructed by ``open_positions`` and then evaluated by
        ``propagate_positions`` before portfolio selection.
    )pbdoc")
        .def(
            py::init<const Market&, const std::vector<int>&, const bool&, const bool&>(),
            py::arg("market"),
            py::arg("trade_signal"),
            py::arg("save_price_data") = false,
            py::arg("debug_mode") = false,
            R"pbdoc(
                Create a new PositionCollection.

                Parameters
                ----------
                market : Market
                    Price and timestamp source for all positions.
                trade_signal : list[int]
                    Market-aligned entry instructions: ``+1`` long, ``-1`` short, ``0`` ignore.
                save_price_data : bool, default=False
                    Whether stop-loss and take-profit histories are recorded.
                debug_mode : bool, default=False
                    Whether native execution diagnostics are printed.
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
        .def("plot", [](const PositionCollection& self, size_t max_positions, bool show) {
            py::object pyplot = py::module_::import("matplotlib.pyplot");
            py::tuple figure_axes = pyplot.attr("subplots")(2, 1, py::arg("sharex") = true);
            py::object axes = figure_axes[1];
            py::object ask_axes = axes.attr("__getitem__")(0);
            py::object bid_axes = axes.attr("__getitem__")(1);
            py::object market = py::cast(const_cast<Market*>(&self.market), py::return_value_policy::reference);
            market.attr("plot_candles")(py::arg("axes") = ask_axes, py::arg("side") = "ask", py::arg("show") = false);
            market.attr("plot_candles")(py::arg("axes") = bid_axes, py::arg("side") = "bid", py::arg("show") = false);
            const size_t count = std::min(max_positions, self.size());
            for (size_t index = 0; index < count; ++index) {
                BasePosition* position = self.__getitem__(index);
                py::object axes_for_position = position->is_long ? ask_axes : bid_axes;
                axes_for_position.attr("axvspan")(position->start_date, position->close_date,
                    py::arg("facecolor") = position->is_long ? "C0" : "C1",
                    py::arg("edgecolor") = "black", py::arg("alpha") = 0.2);
            }
            ask_axes.attr("set_ylabel")("Ask price");
            bid_axes.attr("set_ylabel")("Bid price");
            bid_axes.attr("set_xlabel")("Date");
            if (show) pyplot.attr("show")();
            return py::reinterpret_borrow<py::object>(figure_axes[0]);
        }, py::arg("max_positions") = std::numeric_limits<size_t>::max(), py::arg("show") = true,
        "Plot native ask/bid candles and highlight candidate positions.")
        .def("__repr__", [](const PositionCollection& self) {
            return "<PositionCollection positions=" + std::to_string(self.size())
                + " trade_signals=" + std::to_string(self.number_of_trade) + ">";
        })
        ;
    module.attr("POSITIONCOLLECTION") = module.attr("PositionCollection");
}
