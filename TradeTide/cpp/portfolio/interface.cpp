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

    py::class_<Portfolio>(module, "Portfolio")
        .def(
            py::init<PositionCollection&, BaseCapitalManagement&>(),
            py::arg("position_collection"),
            py::arg("capital_management"),
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

        .def("simulate", &Portfolio::simulate, R"pbdoc(
            Run the full simulation, opening/closing trades according to constraints.
        )pbdoc")

        // Core equity access
        .def("final_equity", &Portfolio::final_equity, R"pbdoc(
            Final equity after simulation.
        )pbdoc")

        .def("peak_equity", &Portfolio::peak_equity, R"pbdoc(
            Highest equity achieved during the simulation.
        )pbdoc")

        .def("equity_curve", &Portfolio::equity_curve, R"pbdoc(
            Time-series of equity over the simulation period.
        )pbdoc")

        .def_readonly("equity", &Portfolio::equity_history, R"pbdoc(
            Raw list of equity values at each step.
        )pbdoc")

        .def_readonly("open_positions_count", &Portfolio::open_position_count, R"pbdoc(
            Number of concurrently open positions over time.
        )pbdoc")

        .def_property_readonly("dates", &Portfolio::get_market_dates,
            py::return_value_policy::reference_internal,
            R"pbdoc(
                List of market timestamps associated with equity and signals.
            )pbdoc")

        .def_property_readonly("market", &Portfolio::get_market, R"pbdoc(
            Access the Market object backing the portfolio.
        )pbdoc")

        .def("get_positions", &Portfolio::get_positions,
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

        // Performance metrics
        .def("calculate_total_return", &Portfolio::calculate_total_return, R"pbdoc(
            Calculate the total return as (final - initial) / initial.
        )pbdoc")

        .def("calculate_annualized_return", &Portfolio::calculate_annualized_return,
             py::arg("total_return"), R"pbdoc(
            Compute the annualized return based on the total return and duration.

            Parameters
            ----------
            total_return : float
                Result from `calculate_total_return`.

            Returns
            -------
            float
                Annualized return (compounded).
        )pbdoc")

        .def("calculate_max_drawdown", &Portfolio::calculate_max_drawdown, R"pbdoc(
            Maximum drawdown as the largest drop from peak equity.
        )pbdoc")

        .def("calculate_sharpe_ratio", &Portfolio::calculate_sharpe_ratio,
             py::arg("risk_free_rate") = 0.0, R"pbdoc(
            Sharpe ratio: mean excess return divided by standard deviation of returns.

            Parameters
            ----------
            risk_free_rate : float, optional
                Risk-free rate to subtract from return (default = 0).

            Returns
            -------
            float
                Sharpe ratio.
        )pbdoc")

        .def("calculate_sortino_ratio", &Portfolio::calculate_sortino_ratio,
             py::arg("risk_free_rate") = 0.0, R"pbdoc(
            Sortino ratio: mean excess return divided by downside deviation.

            Parameters
            ----------
            risk_free_rate : float, optional
                Risk-free rate (default = 0)

            Returns
            -------
            float
                Sortino ratio.
        )pbdoc")

        .def("calculate_win_loss_ratio", &Portfolio::calculate_win_loss_ratio, R"pbdoc(
            Ratio of profitable trades to unprofitable ones.
        )pbdoc")

        .def("calculate_equity", &Portfolio::calculate_equity, R"pbdoc(
            Return the final equity.
        )pbdoc")

        .def("calculate_volatility", &Portfolio::calculate_volatility, R"pbdoc(
            Volatility based on standard deviation of returns.
        )pbdoc")

        .def("calculate_duration", &Portfolio::calculate_duration, R"pbdoc(
            Total time elapsed in the simulation, as a timedelta.
        )pbdoc")

        .def("display", &Portfolio::display, R"pbdoc(
            Total time elapsed in the simulation, as a timedelta.
        )pbdoc")
        ;
}
