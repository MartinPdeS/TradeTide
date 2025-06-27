#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "market.h"  // Update path as needed

PYBIND11_MODULE(interface_market, module) {
    module.doc() = "Python bindings for Market, Bid, and Ask classes used in simulation.";


    pybind11::class_<BasePrices>(module, "BasePrices")
        .def_readonly("open", &BasePrices::open)
        .def_readonly("low", &BasePrices::low)
        .def_readonly("high", &BasePrices::high)
        .def_readonly("close", &BasePrices::close)
    ;

    // ---------------------
    // Market Class
    // ---------------------
    pybind11::class_<Market, std::shared_ptr<Market>>(module, "Market", "Forex market data container for bid/ask prices and simulation time series.")
        .def(pybind11::init<>(), "Create an empty Market object.")

        .def(
            "load_from_csv",
            pybind11::overload_cast<const std::string&, const Duration&>(&Market::load_from_csv),
            pybind11::arg("filename"),
            pybind11::arg("time_span"),
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
        .def_readwrite("ask", &Market::ask, "Get open ask prices.")
        .def_readwrite("bid", &Market::bid, "Get open bid prices.")
        .def_readwrite("start_date", &Market::start_date, "Start date of the market data.")
        .def_readwrite("end_date", &Market::end_date, "End date of the market data.")
        .def_readwrite("pip_value", &Market::pip_value, "Pip value in quote currency.")
        ;
}
