#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "risk_managment.h"

namespace py = pybind11;

PYBIND11_MODULE(interface_risk_managment, module) {
    module.doc() = "Python bindings for the Portfolio class";

    // Bind the RiskManagment class
    py::class_<RiskManagment>(module, "RiskManagment")
        .def(
            py::init<double, double>(),
            py::arg("stop_loss"),
            py::arg("take_profit")
        )
        ;

}