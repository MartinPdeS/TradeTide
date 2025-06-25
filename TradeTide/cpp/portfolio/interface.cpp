#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "portfolio.h"
#include "../metrics/interface.cpp"
#include "../state/interface.cpp"
#include "../record/interface.cpp"

namespace py = pybind11;

PYBIND11_MODULE(interface_portfolio, module) {
    module.doc() = R"pbdoc(
        Python bindings for the Portfolio class.

        This module enables portfolio simulation constrained by capital, risk, and trade limits.
        It allows analyzing equity curves, open positions, and computing risk-adjusted performance metrics.
    )pbdoc"
    ;

    register_metrics(module);

    register_state(module);

    register_record(module);

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
