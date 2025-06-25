#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "strategy.h"


namespace py = pybind11;

PYBIND11_MODULE(interface_strategy, module) {
    module.doc() = "";
}
