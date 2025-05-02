#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "market.h" // Replace with the actual path to your Market class header

namespace py = pybind11;
typedef std::chrono::system_clock::time_point TimePoint;

PYBIND11_MODULE(interface_market, module) {
    py::class_<Ask>(module, "Ask")
        .def_readonly("open", &Ask::open)
        .def_readonly("close", &Ask::close)
        .def_readonly("high", &Ask::high)
        .def_readonly("low", &Ask::low)
    ;

    py::class_<Bid>(module, "Bid")
        .def_readonly("open", &Bid::open)
        .def_readonly("close", &Bid::close)
        .def_readonly("high", &Bid::high)
        .def_readonly("low", &Bid::low)
    ;

    py::class_<Market>(module, "Market")
        .def(
            py::init<const std::string, const TimePoint, const TimePoint, const std::vector<double>&, const std::vector<double>&, const std::vector<double>&, const std::vector<double>&, const double>(),
            py::arg("currencies"),
            py::arg("start_date"),
            py::arg("end_date"),
            py::arg("input_open"),
            py::arg("input_close"),
            py::arg("input_high"),
            py::arg("input_low"),
            py::arg("pip_value")
        )

        // Binding the constructor for random data generation
        .def(py::init<const std::string>(), py::arg("currencies"))

        // Binding member functions
        .def("generate_random_market_data", &Market::generate_random_market_data, py::arg("start"), py::arg("end"), py::arg("interval"))

        .def("display_market_data", &Market::display_market_data)
        .def("load_from_csv", &Market::load_from_csv, py::arg("filename"), py::arg("time_span"))
        .def("set_price_type", &Market::set_prices, py::arg("type"), py::arg("is_bid"))

        // Binding properties
        .def_readwrite("dates", &Market::dates)

        .def_readwrite("start_date", &Market::start_date)
        .def_readwrite("end_date", &Market::end_date)
        .def_readonly("ask", &Market::ask)
        .def_readonly("bid", &Market::bid)
        .def_readonly("spreads", &Market::spreads)
        ;
}
