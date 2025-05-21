#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "market.h"  // Update path as needed

namespace py = pybind11;

PYBIND11_MODULE(interface_market, module) {
    module.doc() = "Python bindings for Market, Bid, and Ask classes used in simulation.";

    // ---------------------
    // Bid Price Class
    // ---------------------
    py::class_<Bid>(module, "Bid", "Bid price data (open, close, high, low, price vector)")
        .def_readonly("open", &Bid::open, "Open bid prices.")
        .def_readonly("close", &Bid::close, "Close bid prices.")
        .def_readonly("high", &Bid::high, "High bid prices.")
        .def_readonly("low", &Bid::low, "Low bid prices.")
        .def_property_readonly("price", &Bid::get_price, "Primary bid price series used for simulation.");

    // ---------------------
    // Ask Price Class
    // ---------------------
    py::class_<Ask>(module, "Ask", "Ask price data (open, close, high, low, price vector)")
        .def_readonly("open", &Ask::open, "Open ask prices.")
        .def_readonly("close", &Ask::close, "Close ask prices.")
        .def_readonly("high", &Ask::high, "High ask prices.")
        .def_readonly("low", &Ask::low, "Low ask prices.")
        .def_property_readonly("price", &Ask::get_price, "Primary ask price series used for simulation.");

    // ---------------------
    // Market Class
    // ---------------------
    py::class_<Market>(module, "Market", "Forex market data container for bid/ask prices and simulation time series.")
        .def(py::init<>(), "Create an empty Market object.")

        .def(
            py::init<
                const std::string,
                const TimePoint,
                const TimePoint,
                const std::vector<double>&,
                const std::vector<double>&,
                const std::vector<double>&,
                const std::vector<double>&,
                const double
            >(),
            py::arg("currencies"),
            py::arg("start_date"),
            py::arg("end_date"),
            py::arg("input_open"),
            py::arg("input_close"),
            py::arg("input_high"),
            py::arg("input_low"),
            py::arg("pip_value"),
            R"pbdoc(
                Create a Market from manually defined price vectors and date range.

                Parameters:
                    currencies (str): Currency pair or symbol.
                    start_date (datetime): Start time of the data.
                    end_date (datetime): End time of the data.
                    input_open (List[float]): Open prices.
                    input_close (List[float]): Close prices.
                    input_high (List[float]): High prices.
                    input_low (List[float]): Low prices.
                    pip_value (float): Pip value in quote currency.
            )pbdoc"
        )

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
            py::overload_cast<
                const std::string&,
                const Duration&,
                std::optional<double>,
                std::optional<bool>
            >(&Market::load_from_csv),
            py::arg("filename"),
            py::arg("time_span"),
            py::arg("spread_override") = std::nullopt,
            py::arg("is_bid_override") = std::nullopt,
            R"pbdoc(
                Load market data from a CSV file.

                Parameters:
                    filename (str): Path to the CSV file.
                    time_span (timedelta): Sampling interval.
                    spread_override (Optional[float]): Use fixed spread if provided.
                    is_bid_override (Optional[bool]): Override header metadata for bid/ask.
            )pbdoc"
        )

        .def("display_market_data", &Market::display_market_data, "Print a preview of the loaded market data.")
        .def("set_price_type", &Market::set_price, py::arg("type"), "Set primary price type: 'open', 'close', etc.")
        .def("set_is_bid", &Market::set_is_bid, py::arg("is_bid"), "Set whether bid prices should be used as the main reference.")

        // Read/write market metadata
        .def_readwrite("dates", &Market::dates, "Vector of datetime timestamps.")
        .def_readwrite("start_date", &Market::start_date, "Start date of the market data.")
        .def_readwrite("end_date", &Market::end_date, "End date of the market data.")
        .def_readwrite("pip_value", &Market::pip_value, "Pip value in quote currency.")
        .def_readonly("ask", &Market::ask, "Ask price object.")
        .def_readonly("bid", &Market::bid, "Bid price object.")
        .def_readonly("spreads", &Market::spreads, "Vector of spread values.");
}
