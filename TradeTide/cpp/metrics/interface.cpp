#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "metrics.h"



void register_metrics(pybind11::module_ &module) {
    pybind11::class_<Metrics>(module, "Metrics")
        .def(
            pybind11::init<>(),
            R"pbdoc(
                Initialize metrics with a reference to the Record object.
            )pbdoc"
        )
        .def(
            "calculate",
            &Metrics::calculate,
            R"pbdoc(
                Calculate and update all performance metrics based on the recorded history.
            )pbdoc"
        )
        .def(
            "display",
            &Metrics::display,
            R"pbdoc(
                Display the final performance metrics in human-readable form.
            )pbdoc"
        )
        .def_readonly("volatility", &Metrics::volatility)
        .def_readonly("total_return", &Metrics::total_return)
        .def_readonly("annualized_return", &Metrics::annualized_return)
        .def_readonly("max_drawdown", &Metrics::max_drawdown)
        .def_readonly("sharpe_ratio", &Metrics::sharpe_ratio)
        .def_readonly("sortino_ratio", &Metrics::sortino_ratio)
        .def_readonly("win_loss_ratio", &Metrics::win_loss_ratio)
        .def_readonly("final_equity", &Metrics::final_equity)
        .def_readonly("peak_equity", &Metrics::peak_equity)
        .def_readonly("total_exected_positions", &Metrics::total_exected_positions)
        .def_readonly("duration", &Metrics::duration)
        ;
}

