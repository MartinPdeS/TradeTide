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


    py::class_<FixedFractionalCapitalManagement, BaseCapitalManagement, std::shared_ptr<FixedFractionalCapitalManagement>>(module, "FixedFractionalCapitalManagement")
        .def(
            py::init<double, double, size_t, double, size_t>(),
            py::arg("capital"),
            py::arg("risk_per_trade"),
            py::arg("max_lot_size"),
            py::arg("max_capital_at_risk"),
            py::arg("max_concurrent_positions"),
            "Create a FixedFractionalCapitalManagement strategy with a given risk percentage per trade.")

        .doc() = R"pbdoc(
            Fixed fractional lot size strategy.

            This strategy risks a fixed fraction of the portfolio equity
            on each trade based on the stop-loss distance.

            Parameters:
                risk_per_trade (float): Fraction of equity to risk per trade (e.g., 0.01 for 1%).
        )pbdoc";
}
