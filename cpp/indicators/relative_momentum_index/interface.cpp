#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cmath>

#include "relative_momentum_index.h"

namespace {

size_t period_from_python(const pybind11::object& value) {
    if (pybind11::isinstance<pybind11::int_>(value)) {
        const auto period = pybind11::cast<size_t>(value);
        if (period == 0) throw pybind11::value_error("Indicator periods must be positive.");
        return period;
    }
    if (pybind11::hasattr(value, "total_seconds")) {
        const double seconds = pybind11::cast<double>(value.attr("total_seconds")());
        const auto period = static_cast<size_t>(std::llround(seconds / 60.0));
        if (period == 0) throw pybind11::value_error("Indicator periods must be positive.");
        return period;
    }
    throw pybind11::type_error("Indicator periods must be bar counts or datetime.timedelta values.");
}

pybind11::object period_as_timedelta(size_t period) {
    return pybind11::module_::import("datetime").attr("timedelta")(pybind11::arg("minutes") = period);
}

}  // namespace

void register_relative_momentum_index(const pybind11::module& module) {

    // RelativeMomentumIndex binding
    pybind11::class_<RelativeMomentumIndex, std::shared_ptr<RelativeMomentumIndex>, BaseIndicator>(module, "RelativeMomentumIndex")
        .def(pybind11::init<>())
        .def(
            pybind11::init<size_t, size_t, double, double>(),
            pybind11::arg("momentum_period"),
            pybind11::arg("smooth_period"),
            pybind11::arg("over_bought"),
            pybind11::arg("over_sold"),
            R"pbdoc(
                Construct a RelativeMomentumIndex indicator.

                Parameters
                ----------
                momentum_period : int
                    Number of periods for momentum calculation.
                smooth_period : int
                    Number of periods for smoothing averages.
                over_bought : float, optional
                    Threshold above which to signal sell (default 70.0).
                over_sold : float, optional
                    Threshold below which to signal buy (default 30.0).
            )pbdoc"
        )
        .def(
            pybind11::init([](
                const pybind11::object& momentum_period,
                const pybind11::object& smooth_window,
                double over_bought,
                double over_sold
            ) {
                return std::make_shared<RelativeMomentumIndex>(
                    period_from_python(momentum_period),
                    period_from_python(smooth_window),
                    over_bought,
                    over_sold
                );
            }),
            pybind11::arg("momentum_period"),
            pybind11::arg("smooth_window"),
            pybind11::arg("over_bought") = 70.0,
            pybind11::arg("over_sold") = 30.0,
            "Compatibility constructor accepting timedelta windows."
        )
        .def_property_readonly("momentum_period", [](const RelativeMomentumIndex& self) {
            return period_as_timedelta(self.momentum_period);
        })
        .def_property_readonly("smooth_window", [](const RelativeMomentumIndex& self) {
            return period_as_timedelta(self.smooth_period);
        })
        .def_property_readonly("over_bought", [](const RelativeMomentumIndex& self) {
            return self.over_bought;
        })
        .def_property_readonly("over_sold", [](const RelativeMomentumIndex& self) {
            return self.over_sold;
        })
        .def_readwrite(
            "_cpp_momentum_period",
            &RelativeMomentumIndex::momentum_period,
            R"pbdoc(
                Number of periods for momentum calculation.

                Attributes
                ----------
                momentum_period : size_t
                    Momentum calculation period.
            )pbdoc"
        )
        .def_readwrite(
            "_cpp_smooth_period",
            &RelativeMomentumIndex::smooth_period,
            R"pbdoc(
                Number of periods for smoothing averages.

                Attributes
                ----------
                smooth_period : size_t
                    Smoothing period for RMI.
            )pbdoc"
        )
        .def_readwrite(
            "_cpp_over_bought",
            &RelativeMomentumIndex::over_bought,
            R"pbdoc(
                Threshold above which to signal sell.

                Attributes
                ----------
                over_bought : float
                    Overbought threshold for RMI.
            )pbdoc"
        )
        .def_readwrite(
            "_cpp_over_sold",
            &RelativeMomentumIndex::over_sold,
            R"pbdoc(
                Threshold below which to signal buy.

                Attributes
                ----------
                over_sold : float
                    Oversold threshold for RMI.
            )pbdoc"
        )
        .def_readonly(
            "_cpp_rmi",
            &RelativeMomentumIndex::rmi,
            R"pbdoc(
                Relative Momentum Index values per time step.

                Attributes
                ----------
                rmi : List[float]
                    Series of RMI values (0–100).
            )pbdoc"
        )
        ;


}
