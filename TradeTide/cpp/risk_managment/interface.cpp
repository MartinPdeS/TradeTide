#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "risk_managment.h"

namespace py = pybind11;

PYBIND11_MODULE(RiskManagmentInterface, module) {
    module.doc() = "Python bindings for the Portfolio class";

    // Bind the RiskManagement class
    py::class_<RiskManagement>(module, "RiskManagement")
        .def(
            py::init<double, double, double, double>(),
            py::arg("initial_balance"),
            py::arg("risk_per_trade"),
            py::arg("stop_loss"),
            py::arg("take_profit")
        )

        .def("calculate_position_size", &RiskManagement::calculate_position_size)
        .def("update_balance", &RiskManagement::update_balance)
        ;

}