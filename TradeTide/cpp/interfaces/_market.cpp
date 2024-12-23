#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "market.cpp" // Replace with the actual path to your Market class header

namespace py = pybind11;
typedef std::chrono::system_clock::time_point TimePoint;

PYBIND11_MODULE(MarketInterface, m) {
    py::class_<Market>(m, "Market")
        // Binding the constructor for predefined data
        .def(py::init<const std::string, const TimePoint, const TimePoint, const std::vector<double>&, const std::vector<double>&, const std::vector<double>&, const std::vector<double>&>(),
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
        .def("generate_random_market_data_days", &Market::generate_random_market_data<std::chrono::days>, py::arg("start"), py::arg("end"))
        .def("generate_random_market_data_minutes", &Market::generate_random_market_data<std::chrono::minutes>, py::arg("start"), py::arg("end"))
        .def("get_open_prices", &Market::get_open_prices)
        .def("get_close_prices", &Market::get_close_prices)
        .def("get_high_prices", &Market::get_high_prices)
        .def("get_low_prices", &Market::get_low_prices)
        .def("display_market_data", &Market::display_market_data)
        .def("load_from_csv", &Market::load_from_csv<std::chrono::minutes>, py::arg("filename"), py::arg("time_span"))
        .def("load_from_csv", &Market::load_from_csv<std::chrono::days>, py::arg("filename"), py::arg("time_span"))

        // Binding properties
        .def_readwrite("start_date", &Market::start_date)
        .def_readwrite("end_date", &Market::end_date);
}
