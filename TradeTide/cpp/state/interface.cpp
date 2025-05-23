#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>

#include "state.h"

namespace py = pybind11;

PYBIND11_MODULE(interface_position, module) {
    module.doc() = "Python bindings for trading positions State and its properties.";

    py::class_<State>(module, "State");
}
