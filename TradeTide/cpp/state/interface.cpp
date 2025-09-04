#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>

#include "state.h"



void register_state(pybind11::module_ &module) {
    pybind11::class_<State>(module, "State")
        .def_readonly("current_date", &State::current_date)
        .def_readonly("equity", &State::equity)
        .def_readonly("capital", &State::capital)
        .def_readonly("number_of_concurent_positions", &State::number_of_concurrent_positions)
        .def_readonly("capital_at_risk", &State::capital_at_risk)
        ;
}
