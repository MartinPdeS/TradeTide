#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "market.h" // Replace with the actual path to your Market class header

namespace py = pybind11;
typedef std::chrono::system_clock::time_point TimePoint;

PYBIND11_MODULE(interface_market, module) {
    py::class_<Market>(module, "Market")
        .def(
            py::init<const std::string, const TimePoint, const TimePoint, const std::vector<double>&, const std::vector<double>&, const std::vector<double>&, const std::vector<double>&>(),
            py::arg("currencies"),
            py::arg("start_date"),
            py::arg("end_date"),
            py::arg("input_open"),
            py::arg("input_close"),
            py::arg("input_high"),
            py::arg("input_low"))

        // Binding the constructor for random data generation
        .def(py::init<const std::string>(), py::arg("currencies"))

        // Binding member functions
        .def("generate_random_market_data", &Market::generate_random_market_data, py::arg("start"), py::arg("end"), py::arg("interval"))

        .def("display_market_data", &Market::display_market_data)
        .def("load_from_csv", &Market::load_from_csv, py::arg("filename"), py::arg("time_span"))

        // Binding properties
        .def_readwrite("open_prices", &Market::open_prices)
        .def_readwrite("close_prices", &Market::close_prices)
        .def_readwrite("low_prices", &Market::low_prices)
        .def_readwrite("high_prices", &Market::high_prices)

        .def_readwrite("start_date", &Market::start_date)
        .def_readwrite("end_date", &Market::end_date)
        ;
}
