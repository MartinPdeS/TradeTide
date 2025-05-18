#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "position_collection.h"


namespace py = pybind11;

PYBIND11_MODULE(interface_position_collection, module) {
    module.doc() = "Python bindings for the PositionCollection class";


    // Bind the Position class
    py::class_<PositionCollection>(module, "PositionCollection")
        .def(
            py::init<const Market&, PipManager&, const Signal&, const bool&>(),
            py::arg("market"),
            py::arg("risk_managment"),
            py::arg("signal"),
            py::arg("save_price_data") = false
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

        .def("__len__", [](PositionCollection &pc){ return pc.positions.size(); })

        .def("get_start_dates", &PositionCollection::get_start_dates)
        .def("get_stop_dates", &PositionCollection::get_stop_dates)
        .def("get_entry_prices", &PositionCollection::get_entry_prices)
        .def("get_exit_prices", &PositionCollection::get_exit_prices)

        .def_readwrite("number_of_trade", &PositionCollection::number_of_trade)
        .def("get_market", &PositionCollection::get_market)
        .def_readonly("save_price_data", &PositionCollection::save_price_data)
        ;
}