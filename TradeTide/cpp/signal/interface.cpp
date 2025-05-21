#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "signal.h"

namespace py = pybind11;

PYBIND11_MODULE(interface_signal, module) {
    module.doc() = "Python bindings for the Signal class, used to represent trading signals aligned with Market data.";

    py::class_<Signal>(module, "Signal", R"pbdoc(
        Signal object representing a sequence of trading decisions over time.

        Each element of the signal is:
        - +1 for a long trade
        - -1 for a short trade
        - 0  for no trade

        The signal is aligned to the time series of a Market object.
    )pbdoc")
        .def(py::init<const Market&>(), py::arg("market"), R"pbdoc(
            Construct a signal object linked to a given Market instance.

            Parameters
            ----------
            market : Market
                A Market instance whose dates define the signal length.
        )pbdoc")

        .def("generate_random", &Signal::generate_random, py::arg("probability"), R"pbdoc(
            Generate a random signal sequence with a given probability of non-zero trades.

            Parameters
            ----------
            probability : float
                Probability that any given timestep will contain a signal (+1 or -1).
        )pbdoc")

        .def("get_signals", &Signal::get_signals, py::return_value_policy::reference_internal, R"pbdoc(
            Return the internal list of trade signals.

            Returns
            -------
            list of int
                Signal values (-1, 0, or 1).
        )pbdoc")

        .def("count_signals", &Signal::count_signals, R"pbdoc(
            Count how many long and short trades are present.

            Returns
            -------
            tuple of int
                (long_count, short_count)
        )pbdoc")

        .def("display", &Signal::display, py::arg("max_count") = 20, R"pbdoc(
            Print a preview of the signal (date and trade direction).

            Parameters
            ----------
            max_count : int, default=20
                Maximum number of entries to display.
        )pbdoc")

        .def("to_csv", &Signal::to_csv, py::arg("filepath"), R"pbdoc(
            Export the signal to a CSV file.

            Parameters
            ----------
            filepath : str
                Destination path for the exported CSV.
        )pbdoc")

        .def("validate_against_market", &Signal::validate_against_market, R"pbdoc(
            Check that the signal length matches the Market data length.

            Returns
            -------
            bool
                True if the signal is valid for the given Market.
        )pbdoc")

        .def("compute_trade_signal", &Signal::compute_trade_signal, R"pbdoc(
            Placeholder function for custom signal computation logic.

            Returns
            -------
            list of int
                The computed signal.
        )pbdoc")

        .def_readonly("market", &Signal::market, R"pbdoc(
            The Market object associated with the signal.
        )pbdoc")

        .def_readwrite("trade_signal", &Signal::trade_signal, R"pbdoc(
            The raw list of trade decisions (-1, 0, 1).
        )pbdoc");
}
