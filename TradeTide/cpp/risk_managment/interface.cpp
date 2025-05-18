#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "risk_managment.h"

namespace py = pybind11;

PYBIND11_MODULE(interface_risk_managment, module) {
    module.doc() = "Python bindings for the Portfolio class";

    py::class_<PipManager>(module, "PipManager");

    // Bind the RiskManagment class
    py::class_<StaticPipManager, PipManager>(module, "StaticPipManager")
        .def(
            py::init<double, double, const bool>(),
            py::arg("stop_loss"),
            py::arg("take_profit"),
            py::arg("save_price_data") = false
        )
        ;

    // Bind the RiskManagment class
    py::class_<TrailingPipManager, PipManager>(module, "TrailingPipManager")
        .def(
            py::init<double, double, const bool>(),
            py::arg("stop_loss"),
            py::arg("take_profit"),
            py::arg("save_price_data") = false
        )
        ;

}