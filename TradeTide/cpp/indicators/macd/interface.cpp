#include <pybind11/pybind11.h>
#include "macd.h"

void register_macd(const pybind11::module& module) {
    pybind11::class_<MACD, std::shared_ptr<MACD>, BaseIndicator>(module, "MACD")
        .def(pybind11::init<size_t, size_t, size_t>(), pybind11::arg("fast_window") = 12, pybind11::arg("slow_window") = 26, pybind11::arg("signal_window") = 9)
        .def_readonly("_cpp_macd", &MACD::macd)
        .def_readonly("_cpp_signal", &MACD::signal)
        .def_readonly("_cpp_histogram", &MACD::histogram);
}
