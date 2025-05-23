#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "capital_management.h"

namespace py = pybind11;

PYBIND11_MODULE(interface_capital_management, module) {
    module.doc() = "Python bindings for capital management strategies (lot sizing).";

    py::class_<BaseCapitalManagement, std::shared_ptr<BaseCapitalManagement>>(module, "BaseCapitalManagement")
        .def(
            "compute_lot_size",
            &BaseCapitalManagement::compute_lot_size,
            py::arg("position"),
            "Compute the lot size for a given position and current equity.")

        .doc() = "Abstract base class for capital (lot size) management strategies.";


    py::class_<FixedFractional, BaseCapitalManagement, std::shared_ptr<FixedFractional>>(module, "FixedFractional")
        .def(
            py::init<double, double, double, size_t>(),
            py::arg("capital"),
            py::arg("risk_per_trade"),
            py::arg("max_capital_at_risk"),
            py::arg("max_concurrent_positions"),
            "Create a FixedFractionalCapitalManagement strategy with a given risk percentage per trade.")

        .doc() = R"pbdoc(
            Fixed fractional lot size strategy.

            This strategy risks a fixed fraction of the portfolio equity
            on each trade based on the stop-loss distance.

            Parameters:
                risk_per_trade (float): Fraction of equity to risk per trade (e.g., 0.01 for 1%).
        )pbdoc"
        ;

        py::class_<FixedLot, BaseCapitalManagement, std::shared_ptr<FixedLot>>(module, "FixedLot")
        .def(py::init<double, double, size_t, size_t>(),
             py::arg("capital"),
             py::arg("fixed_lot_size"),
             py::arg("max_capital_at_risk"),
             py::arg("max_concurrent_positions"),
             "Create a FixedLot strategy with a constant lot size for all trades.")
        .doc() = R"pbdoc(
            Fixed Lot Capital Management Strategy.

            This strategy assigns the same lot size to every trade regardless of equity or risk.
        )pbdoc"
        ;
}
