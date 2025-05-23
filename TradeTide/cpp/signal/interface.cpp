#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "signal.h"

namespace py = pybind11;

PYBIND11_MODULE(interface_signal, module) {
    module.doc() = R"pbdoc(
        Python bindings for the Signal class used to encode time-series trade decisions aligned to Market data.
    )pbdoc";

    py::class_<Signal>(module, "Signal", R"pbdoc(
        Signal represents a vector of trade decisions synchronized with Market timestamps.

        Each signal is:
        - 1 for a long position
        - -1 for a short position
        - 0 for no action

        Useful for backtesting and strategy development.
    )pbdoc")
        .def(py::init<const Market&>(), py::arg("market"), R"pbdoc(
            Create a new Signal instance associated with a given Market.

            Parameters
            ----------
            market : Market
                The market instance whose timestamps the signal will align with.
        )pbdoc")

        .def("generate_random", &Signal::generate_random, py::arg("probability"), R"pbdoc(
            Generate random signals (-1, 0, 1) with specified non-zero probability.

            Parameters
            ----------
            probability : float
                Probability of assigning a trade (long or short) at each time step.
        )pbdoc")

        .def("generate_only_long", &Signal::generate_only_long, py::arg("probability"), R"pbdoc(
            Generate random long-only (1 or 0) signals.

            Parameters
            ----------
            probability : float
                Probability of assigning a long trade (1) at each time step.
        )pbdoc")

        .def("generate_only_short", &Signal::generate_only_short, py::arg("probability"), R"pbdoc(
            Generate random short-only (-1 or 0) signals.

            Parameters
            ----------
            probability : float
                Probability of assigning a short trade (-1) at each time step.
        )pbdoc")

        .def("get_signals", &Signal::get_signals, py::return_value_policy::reference_internal, R"pbdoc(
            Return the internal list of trade signals.

            Returns
            -------
            list[int]
                The list of trade decisions.
        )pbdoc")

        .def("count_signals", &Signal::count_signals, R"pbdoc(
            Count the number of long and short trade signals.

            Returns
            -------
            tuple[int, int]
                (long_count, short_count)
        )pbdoc")

        .def("display", &Signal::display, py::arg("max_count") = 20, R"pbdoc(
            Print the first few signals with corresponding timestamps.

            Parameters
            ----------
            max_count : int, default=20
                Number of signals to print.
        )pbdoc")

        .def("to_csv", &Signal::to_csv, py::arg("filepath"), R"pbdoc(
            Save the signal to a CSV file including metadata.

            Parameters
            ----------
            filepath : str
                Path to the output CSV file.
        )pbdoc")

        .def("validate_against_market", &Signal::validate_against_market, R"pbdoc(
            Validate that the signal vector length matches the market's timestamp vector length.

            Returns
            -------
            bool
                True if valid, False otherwise.
        )pbdoc")

        .def("compute_trade_signal", &Signal::compute_trade_signal, R"pbdoc(
            Return the current signal vector. Placeholder for rule-based logic.

            Returns
            -------
            list[int]
                Current trade signal vector.
        )pbdoc")

        .def_readonly("market", &Signal::market, R"pbdoc(
            Market instance the signal is aligned with.
        )pbdoc")

        .def_readwrite("trade_signal", &Signal::trade_signal, R"pbdoc(
            Raw trade signal list: -1 (short), 0 (neutral), 1 (long).
        )pbdoc");
}
