#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "backtester.h"

namespace py = pybind11;

PYBIND11_MODULE(interface_backtester, module) {
    module.doc() = "Python bindings for the Portfolio class";

    // Bind the Position class
    py::class_<Backtester>(module, "Backtester")
        .def(py::init<>())
        ;

}