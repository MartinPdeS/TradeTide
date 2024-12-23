#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "portfolio.cpp"

namespace py = pybind11;

PYBIND11_MODULE(PortfolioInterface, m) {
    m.doc() = "Python bindings for the Portfolio class";

    // Bind the RiskManagement class
    py::class_<RiskManagement>(m, "RiskManagement")
        .def(py::init<double, double, double, double>(),
             py::arg("initial_balance"),
             py::arg("risk_per_trade"),
             py::arg("stop_loss"),
             py::arg("take_profit"))
        .def("calculate_position_size", &RiskManagement::calculate_position_size)
        .def("update_balance", &RiskManagement::update_balance);

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

    // Bind the Portfolio class
    py::class_<Portfolio>(m, "Portfolio")
        .def(py::init<RiskManagement&>())
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
