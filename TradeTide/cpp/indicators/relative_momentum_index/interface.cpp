#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "relative_momentum_index.h"

void register_relative_momentum_index(const pybind11::module& module) {

    // RelativeMomentumIndex binding
    pybind11::class_<RelativeMomentumIndex, std::shared_ptr<RelativeMomentumIndex>, BaseIndicator>(module, "RELATIVEMOMENTUMINDEX")
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
