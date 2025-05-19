#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "exit_strategy.h"

namespace py = pybind11;

PYBIND11_MODULE(interface_exit_strategy, module) {
    module.doc() = "Python bindings for various exit strategies used in trading positions.";

    py::class_<ExitStrategy, ExitStrategyPtr>(module, "ExitStrategy")
        .doc() = R"pbdoc(
            Abstract base class for SL/TP (stop-loss/take-profit) exit strategies.

            This class is not intended to be used directly. Subclasses implement specific
            behaviors for how stop-loss and take-profit prices are managed over time.
        )pbdoc";

    py::class_<StaticExitStrategy, ExitStrategy, std::shared_ptr<StaticExitStrategy>>(module, "StaticExitStrategy")
        .def(
            py::init<double, double, const bool>(),
            py::arg("stop_loss"),
            py::arg("take_profit"),
            py::arg("save_price_data") = false
        )
        .doc() = R"pbdoc(
            Exit strategy with fixed stop-loss and take-profit levels.

            The SL/TP are set once at entry and do not change over time.

            Parameters:
                stop_loss (float): Distance (in pips) below/above entry to place stop-loss.
                take_profit (float): Distance (in pips) to place take-profit.
                save_price_data (bool): Whether to store SL/TP evolution data.
        )pbdoc";

    py::class_<TrailingExitStrategy, ExitStrategy, std::shared_ptr<TrailingExitStrategy>>(module, "TrailingExitStrategy")
        .def(
            py::init<double, double, const bool>(),
            py::arg("stop_loss"),
            py::arg("take_profit"),
            py::arg("save_price_data") = false
        )
        .doc() = R"pbdoc(
            Exit strategy with dynamically adjusted trailing stop-loss.

            The stop-loss follows the market price when the trade is in profit, but never retreats.
            Take-profit remains fixed.

            Parameters:
                stop_loss (float): Distance (in pips) from market to stop-loss.
                take_profit (float): Distance (in pips) from entry to take-profit.
                save_price_data (bool): Whether to store SL/TP evolution data.
        )pbdoc";

    py::class_<BreakEvenExitStrategy, ExitStrategy, std::shared_ptr<BreakEvenExitStrategy>>(module, "BreakEvenExitStrategy")
        .def(
            py::init<double, double, double, const bool>(),
            py::arg("stop_loss"),
            py::arg("take_profit"),
            py::arg("break_even_trigger_pip"),
            py::arg("save_price_data") = false
        )
        .doc() = R"pbdoc(
            Exit strategy that moves stop-loss to break-even after a favorable move.

            The stop-loss starts at a fixed distance from entry. Once the trade has moved
            `break_even_trigger_pip` pips in profit, the stop-loss is adjusted to the entry price.

            Parameters:
                stop_loss (float): Initial stop-loss distance (in pips).
                take_profit (float): Take-profit distance (in pips).
                break_even_trigger_pip (float): Distance in pips required to trigger break-even.
                save_price_data (bool): Whether to store SL/TP evolution data.
        )pbdoc";
}
