#include <pybind11/pybind11.h>
#include "relative_strength_index.h"

void register_relative_strength_index(const pybind11::module& module) {
    pybind11::class_<RelativeStrengthIndex, std::shared_ptr<RelativeStrengthIndex>, BaseIndicator>(module, "RELATIVESTRENGTHINDEX")
        .def(pybind11::init<size_t, double, double>(), pybind11::arg("window"), pybind11::arg("over_bought") = 70.0, pybind11::arg("over_sold") = 30.0)
        .def_readonly("_cpp_rsi", &RelativeStrengthIndex::rsi)
        .def_readonly("_cpp_over_bought", &RelativeStrengthIndex::over_bought)
        .def_readonly("_cpp_over_sold", &RelativeStrengthIndex::over_sold);
}
