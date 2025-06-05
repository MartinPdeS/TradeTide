#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "portfolio.h"
#include "../position_collection/position_collection.h"

namespace py = pybind11;

PYBIND11_MODULE(interface_portfolio, module) {
    module.doc() = R"pbdoc(
        Python bindings for the Portfolio class.

        This module enables portfolio simulation constrained by capital, risk, and trade limits.
        It allows analyzing equity curves, open positions, and computing risk-adjusted performance metrics.
    )pbdoc"
    ;

    py::class_<Metrics>(module, "Metrics")
        .def(
            py::init<>(),
            R"pbdoc(
                Initialize metrics with a reference to the Record object.
            )pbdoc"
        )
        .def(
            "calculate",
            &Metrics::calculate,
            R"pbdoc(
                Calculate and update all performance metrics based on the recorded history.
            )pbdoc"
        )
        .def(
            "display",
            &Metrics::display,
            R"pbdoc(
                Display the final performance metrics in human-readable form.
            )pbdoc"
        )
        .def_readonly("volatility", &Metrics::volatility)
        .def_readonly("total_return", &Metrics::total_return)
        .def_readonly("annualized_return", &Metrics::annualized_return)
        .def_readonly("max_drawdown", &Metrics::max_drawdown)
        .def_readonly("sharpe_ratio", &Metrics::sharpe_ratio)
        .def_readonly("sortino_ratio", &Metrics::sortino_ratio)
        .def_readonly("win_loss_ratio", &Metrics::win_loss_ratio)
        .def_readonly("final_equity", &Metrics::final_equity)
        .def_readonly("peak_equity", &Metrics::peak_equity)
        .def_readonly("total_exected_positions", &Metrics::total_exected_positions)
        .def_readonly("duration", &Metrics::duration)
        ;

    py::class_<State>(module, "State")
        .def_readonly("current_date", &State::current_date)
        .def_readonly("equity", &State::equity)
        .def_readonly("capital", &State::capital)
        .def_readonly("number_of_concurent_positions", &State::number_of_concurrent_positions)
        .def_readonly("capital_at_risk", &State::capital_at_risk)
        ;

    py::class_<Record>(module, "Record")
        .def_readonly("time", &Record::time)
        .def_readonly("equity", &Record::equity)
        .def_readonly("capital", &Record::capital)
        .def_readonly("number_of_concurent_positions", &Record::concurrent_positions)
        .def_readonly("capital_at_risk", &Record::capital_at_risk)
        .def_readonly("initial_capital", &Record::initial_capital)
        ;

    py::class_<Portfolio>(module, "PORTFOLIO")
        .def(
            py::init<PositionCollection&>(),
            py::arg("position_collection"),
            R"pbdoc(
                Create a portfolio simulator using a predefined position collection and capital management strategy.

                Parameters
                ----------
                position_collection : PositionCollection
                    The set of all candidate trades.
                capital_management : BaseCapitalManagement
                    Object that defines risk, lot sizing, and exposure limits.
            )pbdoc"
        )
        .def("simulate",
            &Portfolio::simulate,
            py::arg("capital_management"),
            R"pbdoc(
                Run the full simulation, opening/closing trades according to constraints.
            )pbdoc"
        )
        .def_readonly(
            "state",
            &Portfolio::state,
            py::return_value_policy::reference_internal,
            R"pbdoc(
                Access the current state of the portfolio, including equity and position count.
            )pbdoc"
        )
        .def_readonly(
            "record",
            &Portfolio::record,
            py::return_value_policy::reference_internal,
            R"pbdoc(
                Access the Record object containing historical state data.
            )pbdoc"
        )
        .def_property_readonly(
            "market",
            &Portfolio::get_market,
            py::return_value_policy::reference_internal,
            R"pbdoc(
                Access the Market object backing the portfolio.
            )pbdoc"
        )
        .def(
            "get_metrics",
            &Portfolio::get_metrics,
            py::return_value_policy::move,
            R"pbdoc(
                Access the Metrics object containing performance metrics.
            )pbdoc"
        )
        .def(
            "get_positions",
            &Portfolio::get_positions,
            py::arg("count") = std::numeric_limits<size_t>::max(),
            py::return_value_policy::reference_internal,
            R"pbdoc(
                Get the list of activated positions up to an optional maximum.

                Parameters
                ----------
                count : int, optional
                    Maximum number of positions to return (default = all)

                Returns
                -------
                List[BasePosition]
                    Positions selected by the portfolio during simulation.
            )pbdoc")
        .def(
            "display",
            &Portfolio::display,
            R"pbdoc(
                Total time elapsed in the simulation, as a timedelta.
            )pbdoc"
        )
        ;
}
