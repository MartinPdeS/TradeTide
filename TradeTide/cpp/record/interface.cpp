#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>

#include "record.h"

namespace py = pybind11;

PYBIND11_MODULE(interface_record, module) {
    module.doc() = "Python bindings for trading positions State and its properties.";

    py::class_<Record>(module, "Record");
}
