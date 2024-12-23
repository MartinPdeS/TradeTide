#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "portfolio.cpp"
#include "risk_managment.cpp"

namespace py = pybind11;

PYBIND11_MODULE(PortfolioInterface, m) {
    m.doc() = "Python bindings for the Portfolio class";

    // Bind the Portfolio class
    py::class_<Portfolio>(m, "Portfolio")
        .def(py::init<RiskManagement&>(), py::arg("risk_manager"))
        .def("add_position", &Portfolio::add_position,
             py::arg("is_long"),
             py::arg("entry_price"),
             py::arg("pip_price"),
             py::arg("lot_size"),
             py::arg("stop_loss"),
             py::arg("take_profit")
             )
        .def("process_signals", &Portfolio::process_signals)
        .def("update_capital", &Portfolio::update_capital)
        .def("display_positions", &Portfolio::display_positions)
        .def("get_capital", &Portfolio::get_capital)
        .def("get_entry_prices", &Portfolio::get_entry_prices)
        .def("get_exit_prices", &Portfolio::get_exit_prices)
        .def("get_open_dates", &Portfolio::get_open_dates)
        .def("get_close_dates", &Portfolio::get_close_dates);
}
