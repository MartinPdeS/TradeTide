#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>

#include "record.h"

void register_record(pybind11::module_ &module) {
    pybind11::class_<Record>(module, "Record")
        .def_readonly("time", &Record::time)
        .def_readonly("equity", &Record::equity)
        .def_readonly("capital", &Record::capital)
        .def_readonly("concurrent_positions", &Record::concurrent_positions)
        .def_readonly("capital_at_risk", &Record::capital_at_risk)
        .def_readonly("initial_capital", &Record::initial_capital)
        ;
}
