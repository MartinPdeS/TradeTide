#include <pybind11/pybind11.h>
#include "relative_strength_index.h"

void register_relative_strength_index(const pybind11::module& module) {
    pybind11::class_<RelativeStrengthIndex, std::shared_ptr<RelativeStrengthIndex>, BaseIndicator>(
        module, "RELATIVESTRENGTHINDEX", R"pbdoc(
        Relative Strength Index (RSI) calculated with Wilder smoothing.

        The indicator emits ``+1`` for oversold values, ``-1`` for overbought
        values, and ``0`` otherwise. Call ``_cpp_run_with_vector`` or
        ``_cpp_run_with_market`` before reading ``_cpp_rsi``.
        )pbdoc")
        .def(pybind11::init<size_t, double, double>(), pybind11::arg("window"), pybind11::arg("over_bought") = 70.0, pybind11::arg("over_sold") = 30.0, R"pbdoc(
            Parameters
            ----------
            window : int
                Number of observations used by Wilder smoothing.
            over_bought : float, default=70.0
                RSI threshold above which a sell region is emitted.
            over_sold : float, default=30.0
                RSI threshold below which a buy region is emitted.
        )pbdoc")
        .def_readonly("_cpp_rsi", &RelativeStrengthIndex::rsi, "RSI values; warm-up entries are NaN.")
        .def_readonly("_cpp_over_bought", &RelativeStrengthIndex::over_bought, "Upper RSI threshold.")
        .def_readonly("_cpp_over_sold", &RelativeStrengthIndex::over_sold, "Lower RSI threshold.")
        .def("__repr__", [](const RelativeStrengthIndex& self) {
            return "<RelativeStrengthIndex window=" + std::to_string(self.window)
                + " over_bought=" + std::to_string(self.over_bought)
                + " over_sold=" + std::to_string(self.over_sold) + ">";
        });
}
