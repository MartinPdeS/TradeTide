#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "position.h"
#include "../risk_managment/risk_managment.h"

namespace py = pybind11;

PYBIND11_MODULE(interface_position, module) {
    module.doc() = "Python bindings for the Position class";

    py::class_<BasePosition>(module, "BasePosition")
        .def_readwrite("entry_price", &BasePosition::entry_price)
        .def_readwrite("lot_size", &BasePosition::lot_size)
        .def_readwrite("entry_price", &BasePosition::entry_price)
        .def_readwrite("start_date", &BasePosition::start_date)
        .def_readwrite("close_date", &BasePosition::close_date)
        .def("display", &BasePosition::display)
        .def("calculate_profite_and_loss", &BasePosition::calculate_profite_and_loss)
        .def_readonly("is_closed", &BasePosition::is_closed)
        .def("stop_loss_prices", &BasePosition::stop_loss_prices)
        .def("take_profit_prices", &BasePosition::take_profit_prices)
        .def("dates", &BasePosition::dates)
    ;

    py::class_<Long, BasePosition>(module, "Long");

    py::class_<Short, BasePosition>(module, "Short");


}