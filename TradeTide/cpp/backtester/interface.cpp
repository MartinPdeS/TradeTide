#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "backtester.h"


PYBIND11_MODULE(backtester, module) {
    module.doc() = "Native orchestration API for complete TradeTide backtests.";

    pybind11::class_<Backtester>(module, "Backtester", R"pbdoc(
        End-to-end backtesting orchestrator.

        It derives strategy signals, creates and propagates positions, then
        simulates their execution under the supplied capital-management rules.
    )pbdoc")
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
    .def("__repr__", [](const Backtester& self) {
        return "<Backtester market_observations=" + std::to_string(self.market.dates.size())
            + " completed=" + (self.portfolio.record.equity.empty() ? "False" : "True") + ">";
    })
    ;
    module.attr("BACKTESTER") = module.attr("Backtester");

}
