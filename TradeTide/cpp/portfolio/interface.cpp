#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "portfolio.h"
#include "../position_collection/position_collection.h"  // if needed

namespace py = pybind11;

PYBIND11_MODULE(interface_portfolio, module) {
    module.doc() = R"pbdoc(
        Python bindings for the Portfolio class.

        This module allows capital-constrained portfolio simulation using
        a collection of candidate trading positions and defined risk limits.
    )pbdoc";

    py::class_<Portfolio>(module, "Portfolio")
        .def(
            py::init<PositionCollection&, double, size_t, double, double>(),
            py::arg("position_collection"),
            py::arg("initial_capital"),
            py::arg("max_concurrent_positions"),
            py::arg("max_lot_size"),
            py::arg("max_capital_at_risk"),
            R"pbdoc(
                Initialize a new Portfolio simulation.

                Args:
                    position_collection (PositionCollection): The set of candidate trades to consider.
                    initial_capital (float): Starting capital.
                    max_concurrent_positions (int): Maximum number of open positions allowed at any time.
                    max_lot_size (float): Maximum allowable lot size per trade.
                    max_capital_at_risk (float): Maximum fraction of capital to risk per trade.
            )pbdoc"
        )

        .def("simulate", &Portfolio::simulate,
            R"pbdoc(
                Run the full portfolio simulation.

                This method processes the entire time series, opening and closing positions
                as allowed by the risk and capital constraints.
            )pbdoc")

        .def("final_equity", &Portfolio::final_equity,
            R"pbdoc(
                Get the final portfolio equity after simulation.

                Returns:
                    float: Final capital after all trades.
            )pbdoc")

        .def("peak_equity", &Portfolio::peak_equity,
            R"pbdoc(
                Get the peak portfolio equity achieved during simulation.

                Returns:
                    float: Maximum recorded equity during simulation.
            )pbdoc")

        .def("equity_curve", &Portfolio::equity_curve,
            R"pbdoc(
                Return the full equity time series.

                Returns:
                    List[float]: Equity value at each time step.
            )pbdoc")

        .def("display", &Portfolio::display,
            R"pbdoc(
                Print a summary of portfolio performance to the console.
            )pbdoc")

        .def("open_position_count_over_time", &Portfolio::open_position_count_over_time,
            R"pbdoc(
                Returns a list indicating how many positions were open at each market time step.

                Returns:
                    List[int]: Number of open positions aligned with market timestamps.
            )pbdoc")

        .def("get_market_dates", &Portfolio::get_market_dates,
            py::return_value_policy::reference_internal,
            R"pbdoc(
                Return the list of market timestamps used in the portfolio.

                Returns:
                    List[datetime]: Time series aligned with market data and position signals.
            )pbdoc")

        .def("get_equity_over_time", &Portfolio::equity_over_time,
            R"pbdoc(
                Returns a list of equity values over time.

                Returns:
                    List[float]: Portfolio equity at each market time step, including realized PnL.
            )pbdoc")


        ;
}
