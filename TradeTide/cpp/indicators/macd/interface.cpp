#include <pybind11/pybind11.h>
#include "macd.h"

void register_macd(const pybind11::module& module) {
    pybind11::class_<MACD, std::shared_ptr<MACD>, BaseIndicator>(module, "MACD", R"pbdoc(
        Moving Average Convergence Divergence (MACD) indicator.

        Regions are emitted only at histogram zero crossovers: ``+1`` for a
        bullish crossover and ``-1`` for a bearish crossover.
    )pbdoc")
        .def(pybind11::init<size_t, size_t, size_t>(), pybind11::arg("fast_window") = 12, pybind11::arg("slow_window") = 26, pybind11::arg("signal_window") = 9, R"pbdoc(
            Parameters
            ----------
            fast_window : int, default=12
                Span of the fast exponential moving average.
            slow_window : int, default=26
                Span of the slow exponential moving average; must exceed fast_window.
            signal_window : int, default=9
                Span of the EMA applied to the MACD line.
        )pbdoc")
        .def_readonly("_cpp_macd", &MACD::macd, "MACD line values; warm-up entries are NaN.")
        .def_readonly("_cpp_signal", &MACD::signal, "Signal-line values; warm-up entries are NaN.")
        .def_readonly("_cpp_histogram", &MACD::histogram, "MACD minus signal-line values.")
        .def("__repr__", [](const MACD& self) {
            return "<MACD fast_window=" + std::to_string(self.fast_window)
                + " slow_window=" + std::to_string(self.slow_window)
                + " signal_window=" + std::to_string(self.signal_window) + ">";
        });
}
