#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "position_collection.h"


namespace py = pybind11;

PYBIND11_MODULE(interface_position_collection, module) {
    module.doc() = "Python bindings for the PositionCollection class";


    py::class_<BasePosition>(module, "BasePosition")
        .def_readwrite("entry_price", &BasePosition::entry_price)
        .def_readwrite("lot_size", &BasePosition::lot_size)
        .def_readwrite("entry_price", &BasePosition::entry_price)
        .def_readwrite("start_date", &BasePosition::start_date)
        .def_readwrite("close_date", &BasePosition::close_date)
        .def("display", &BasePosition::display)
        .def("calculate_profite_and_loss", &BasePosition::calculate_profite_and_loss)
    ;



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
        .def("terminate_open_positions", &PositionCollection::terminate_open_positions)

        .def("__getitem__",
            [](PositionCollection &self, size_t i) -> BasePosition* {
                if (i >= self.positions.size())
                    throw py::index_error("Index out of range");
                return self.positions[i].get();                   // return pointer
            },
            py::return_value_policy::reference_internal       // keep parent alive
       )

        .def("get_start_dates", &PositionCollection::get_start_dates)
        .def("get_stop_dates", &PositionCollection::get_stop_dates)
        .def("get_entry_prices", &PositionCollection::get_entry_prices)
        .def("get_exit_prices", &PositionCollection::get_exit_prices)

        .def_readwrite("number_of_trade", &PositionCollection::number_of_trade)
        .def("get_market", &PositionCollection::get_market)
        ;
}