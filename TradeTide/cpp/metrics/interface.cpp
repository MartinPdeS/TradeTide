#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "metrics.h"


namespace py = pybind11;

PYBIND11_MODULE(interface_portfolio, module) {
    module.doc() = "";
}
