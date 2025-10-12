#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "backtester.h"


PYBIND11_MODULE(interface_backtester, module) {

    pybind11::class_<Backtester>(module, "BACKTESTER")
    .def(pybind11::init<Strategy&, ExitStrategy&, Market&, BaseCapitalManagement&, const bool>(),
        pybind11::arg("strategy"),
        pybind11::arg("exit_strategy"),
        pybind11::arg("market"),
        pybind11::arg("capital_management"),
        pybind11::arg("debug_mode") = false,
        R"pbdoc(
            Create a new Backtester instance.

        Parameters
        ----------
        strategy : Strategy
            The trading strategy to be applied.
        exit_strategy : ExitStrategy
            The exit strategy for managing positions.
        market : Market
            The market data reference.
        capital_management : BaseCapitalManagement
            The capital management strategy to use.
        )pbdoc"
     )
    .def("run",
        &Backtester::run,
        "Run the backtesting simulation."
    )
    .def("print_performance",
        &Backtester::print_performance,
        "Print the performance metrics of the backtest."
    )
    .def_readonly("_cpp_portfolio",
        &Backtester::portfolio,
        "The portfolio being managed."
    )
    .def_readonly("_cpp_position_collection",
        &Backtester::position_collection,
        "The collection of positions being tracked."
    )
    .def_readonly("_cpp_strategy",
        &Backtester::strategy,
        "The strategy being applied during backtesting."
    )
    .def_readonly("_cpp_market",
        &Backtester::market,
        "The market data reference used in the backtesting."
    )
    .def("print_summary",
        &Backtester::print_summary,
        "Print the summary metrics of the backtest."
    )
    .def("print_basic_info",
        &Backtester::print_basic_info,
        "Print basic information about the backtest."
    )
    .def("print_run_times",
        &Backtester::print_run_times,
        "Print the execution times for each phase of the backtest."
    )
    ;

}
