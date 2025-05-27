#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "market.h"  // Update path as needed

namespace py = pybind11;

PYBIND11_MODULE(interface_market, module) {
    module.doc() = "Python bindings for Market, Bid, and Ask classes used in simulation.";


    // ---------------------
    // Market Class
    // ---------------------
    py::class_<Market>(module, "Market", "Forex market data container for bid/ask prices and simulation time series.")
        .def(py::init<>(), "Create an empty Market object.")

        .def(
            "generate_random_market_data",
            &Market::generate_random_market_data,
            py::arg("start"),
            py::arg("end"),
            py::arg("interval"),
            "Generate synthetic random market data between start and end with given interval."
        )

        .def(
            "load_from_csv",
            py::overload_cast<const std::string&, const Duration&>(&Market::load_from_csv),
            py::arg("filename"),
            py::arg("time_span"),
            R"pbdoc(
                Load market data from a CSV file.

                Parameters:
                    filename (str): Path to the CSV file.
                    time_span (timedelta): Sampling interval.
                    spread_override (Optional[float]): Use fixed spread if provided.
                    is_bid_override (Optional[bool]): Override header metadata for bid/ask.
            )pbdoc"
        )

        .def("display", &Market::display_market_data, "Print a preview of the loaded market data.")

        // Read/write market metadata
        .def_readwrite("dates", &Market::dates, "Vector of datetime timestamps.")
        .def_readwrite("ask_open", &Market::ask_open, "Get open ask prices.")
        .def_readwrite("ask_high", &Market::ask_high, "Get high ask prices.")
        .def_readwrite("ask_low", &Market::ask_low, "Get low ask prices.")
        .def_readwrite("ask_close", &Market::ask_close, "Get close ask prices.")
        .def_readwrite("bid_open", &Market::bid_open, "Get open bid prices.")
        .def_readwrite("bid_high", &Market::bid_high, "Get high bid prices.")
        .def_readwrite("bid_low", &Market::bid_low, "Get low bid prices.")
        .def_readwrite("bid_close", &Market::bid_close, "Get close bid prices.")
        .def_readwrite("start_date", &Market::start_date, "Start date of the market data.")
        .def_readwrite("end_date", &Market::end_date, "End date of the market data.")
        .def_readwrite("pip_value", &Market::pip_value, "Pip value in quote currency.")
        ;
}
