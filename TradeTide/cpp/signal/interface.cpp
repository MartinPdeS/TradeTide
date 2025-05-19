#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "signal.h"

namespace py = pybind11;

PYBIND11_MODULE(interface_signal, module) {
    module.doc() = "Python bindings for the Signal class";

    // Bind the Position class
    py::class_<Signal>(module, "Signal")
        .def(
            py::init<const Market&>(),
            py::arg("market")
        )

        .def("generate_random", &Signal::generate_random, py::arg("probability"))
        .def("display", &Signal::display)

        .def_readwrite("trade_signal", &Signal::trade_signal)

        ;

}