#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "base_indicator.h"

void register_base_indicator(const pybind11::module& module) {

    // BaseIndicator binding
    pybind11::class_<BaseIndicator, std::shared_ptr<BaseIndicator>>(module, "BaseIndicator")
        .def(
            "_cpp_run_with_market",
            &BaseIndicator::run_with_market,
            pybind11::arg("market"),
            R"pbdoc(
                Run the indicator on market data.

                Parameters
                ----------
                market : Market
                    Market data containing price series (e.g., market.ask.close).
            )pbdoc"
        )
        .def(
            "_cpp_run_with_vector",
            &BaseIndicator::run_with_vector,
            pybind11::arg("prices"),
            R"pbdoc(
                Run the indicator on a raw price vector.

                Parameters
                ----------
                prices : List[float]
                    Time series of price values.
            )pbdoc"
        )
        .def_readonly(
            "_cpp_regions",
            &BaseIndicator::regions,
            pybind11::return_value_policy::reference_internal,
            R"pbdoc(
                Trade signal array.

                Attributes
                ----------
                signals : List[int]
                    +1 for buy signal, -1 for sell signal, 0 otherwise.
            )pbdoc"
        )
        ;

}
