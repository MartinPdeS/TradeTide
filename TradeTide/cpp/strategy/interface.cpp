#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "strategy.h"


PYBIND11_MODULE(interface_strategy, module) {
    module.doc() = "";

    // Strategy binding
    pybind11::class_<Strategy>(module, "STRATEGY")
        .def(pybind11::init<>())
        .def(
            "add_indicator",
            &Strategy::add_indicator,
            pybind11::arg("indicator"),
            R"pbdoc(
                Add an indicator to the strategy.
                This method allows adding a custom indicator to the strategy for processing market data.
                Parameters
                ----------
                indicator : BaseIndicator
                    A shared pointer to the BaseIndicator instance to be added.
            )pbdoc"
        )
        .def(
            "get_trade_signal",
            &Strategy::get_trade_signal,
            pybind11::return_value_policy::reference_internal,
            pybind11::arg("market"),
            R"pbdoc(
                Get the trade signal based on the current market data.
                This method runs all indicators with the provided market data and computes a consensus signal.
                Parameters
                ----------
                market : Market
                    The market data containing prices to analyze.
                Returns
                -------
                List[int]
                    A vector of integers representing the trade signals from each indicator.
            )pbdoc"
        )
    ;
}
