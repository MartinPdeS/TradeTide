#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "position_collection.h"


namespace py = pybind11;

PYBIND11_MODULE(interface_position_collection, module) {
    module.doc() = "Python bindings for the PositionCollection class";

    // Bind the Position class
    py::class_<PositionCollection>(module, "PositionCollection")
        .def(
            py::init<const Market&, const RiskManagment&, const Signal&>(),
            py::arg("market"),
            py::arg("risk_managment"),
            py::arg("signal")
        )

        .def("open_positions", &PositionCollection::open_positions)
        .def("close_positions", &PositionCollection::close_positions)
        .def("display", &PositionCollection::display)

        .def("get_start_dates", &PositionCollection::get_start_dates)
        .def("get_stop_dates", &PositionCollection::get_stop_dates)
        .def("get_entry_prices", &PositionCollection::get_entry_prices)
        .def("get_exit_prices", &PositionCollection::get_exit_prices)

        .def_readwrite("number_of_trade", &PositionCollection::number_of_trade)
        .def_readonly("market", &PositionCollection::market)
        ;
}