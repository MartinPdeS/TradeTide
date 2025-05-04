#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "position.h"
#include "../risk_managment/risk_managment.h"

namespace py = pybind11;

PYBIND11_MODULE(interface_position, module) {
    module.doc() = "Python bindings for the Portfolio class";

    // Bind the Position class
    py::class_<Position, std::shared_ptr<Position>>(module, "Position")
        .def(
            py::init<bool, double, double, double, double, double>(),
            py::arg("is_long"),
            py::arg("entry_price"),
            py::arg("lot_size"),
            py::arg("pip_price"),
            py::arg("stop_loss"),
            py::arg("take_profit")
        )
        .def("display", &Position::display)
        .def("calculate_profite_and_loss", &Position::calculate_profite_and_loss)

        .def_readwrite("entry_price", &Position::entry_price)
        .def_readwrite("lot_size", &Position::lot_size)
        .def_readwrite("pip_price", &Position::pip_price)
        .def_readwrite("entry_price", &Position::entry_price)
        ;


    py::class_<BasePosition>(module, "BasePosition")
        .def_readwrite("entry_price", &BasePosition::entry_price)
        .def_readwrite("lot_size", &BasePosition::lot_size)
        .def_readwrite("entry_price", &BasePosition::entry_price)
        .def_readwrite("start_date", &BasePosition::start_date)
        .def_readwrite("close_date", &BasePosition::close_date)
        .def("display", &BasePosition::display)
        .def("calculate_profite_and_loss", &BasePosition::calculate_profite_and_loss)
    ;


    py::class_<Long, BasePosition>(module, "Long")
        .def(
            py::init<const Market&, const RiskManagment&, const double, const size_t>(),
            py::arg("market"),
            py::arg("risk_managment"),
            py::arg("lot_size"),
            py::arg("start_idx")
        )
        ;

        py::class_<Short, BasePosition>(module, "Long")
        .def(
            py::init<const Market&, const RiskManagment&, const double, const size_t>(),
            py::arg("market"),
            py::arg("risk_managment"),
            py::arg("lot_size"),
            py::arg("start_idx")
        )
        ;



}