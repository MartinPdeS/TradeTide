#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "position.cpp"

namespace py = pybind11;

PYBIND11_MODULE(PositionInterface, m) {
    m.doc() = "Python bindings for the Portfolio class";

    // Bind the Position class
    py::class_<Position, std::shared_ptr<Position>>(m, "Position")
        .def(py::init<bool, double, double, double, double, double>(),
            py::arg("is_long"),
            py::arg("entry_price"),
            py::arg("lot_size"),
            py::arg("pip_price"),
            py::arg("stop_loss"),
            py::arg("take_profit"))
        .def("display", &Position::display)
        .def("calculate_pnl", &Position::calculate_pnl);

}