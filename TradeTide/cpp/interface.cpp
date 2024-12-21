#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "portfolio.cpp"

namespace py = pybind11;

PYBIND11_MODULE(PortfolioInterface, m) {
    m.doc() = "Python bindings for the Portfolio class";

    // Bind the RiskManagement class
    py::class_<RiskManagement>(m, "RiskManagement")
        .def(py::init<double, double, double>(), 
             py::arg("initial_balance"), 
             py::arg("risk_per_trade"), 
             py::arg("stop_loss"))
        .def("calculate_position_size", &RiskManagement::calculate_position_size)
        .def("update_balance", &RiskManagement::update_balance);

    // Bind the Position class
    py::class_<Position, std::shared_ptr<Position>>(m, "Position")
        .def(py::init<const std::string&, bool, double, double, double>(),
             py::arg("currency_pair"), py::arg("is_long"), py::arg("entry_price"), 
             py::arg("lot_size"), py::arg("account_balance"))
        .def("display", &Position::display)
        .def("calculate_pnl", &Position::calculate_pnl);

    // Bind the Portfolio class
    py::class_<Portfolio>(m, "Portfolio")
        .def(py::init<RiskManagement&>(), py::arg("risk_manager"))
        .def("add_position", &Portfolio::add_position, 
             py::arg("currency_pair"), 
             py::arg("is_long"), 
             py::arg("entry_price"), 
             py::arg("pip_value"))
        .def("display_positions", &Portfolio::display_positions)
        .def("update_capital", &Portfolio::update_capital)
        .def("calculate_total_pnl", &Portfolio::calculate_total_pnl)
        .def("calculate_roi", &Portfolio::calculate_roi)
        .def("calculate_sharpe_ratio", &Portfolio::calculate_sharpe_ratio)
        .def("calculate_max_drawdown", &Portfolio::calculate_max_drawdown)
        .def("calculate_win_rate", &Portfolio::calculate_win_rate)
        .def("print_metrics", &Portfolio::print_metrics, py::arg("risk_free_rate"))
        .def("get_capital", &Portfolio::get_capital);
}
