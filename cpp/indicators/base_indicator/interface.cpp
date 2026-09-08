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
            "run",
            &BaseIndicator::run_with_market,
            pybind11::arg("market"),
            "Run the indicator on native market data."
        )
        .def_property_readonly(
            "market",
            [](const BaseIndicator& self) { return self.market; },
            pybind11::return_value_policy::reference
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
        .def(
            "plot",
            [](const BaseIndicator& self, bool show) {
                pybind11::object pyplot = pybind11::module_::import("matplotlib.pyplot");
                pybind11::tuple figure_axes = pyplot.attr("subplots")();
                pybind11::object axes = figure_axes[1];
                pybind11::list indices;
                for (size_t index = 0; index < self.regions.size(); ++index) indices.append(index);
                axes.attr("step")(indices, pybind11::cast(self.regions), pybind11::arg("where") = "mid", pybind11::arg("label") = "Signal");
                axes.attr("set_xlabel")("Bar");
                axes.attr("set_ylabel")("Signal");
                axes.attr("set_yticks")(pybind11::make_tuple(-1, 0, 1));
                axes.attr("legend")();
                if (show) pyplot.attr("show")();
                // ``tuple[index]`` is a borrowed handle.  Return an owned
                // reference because ``figure_axes`` is destroyed on return.
                return pybind11::reinterpret_borrow<pybind11::object>(figure_axes[0]);
            },
            pybind11::arg("show") = true,
            "Plot the indicator's generated buy/sell signal regions."
        )
        ;

}
