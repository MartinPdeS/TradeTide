#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cmath>

#include "bollinger_bands.h"

namespace {

size_t window_from_python(const pybind11::object& value) {
    if (pybind11::isinstance<pybind11::int_>(value)) {
        const auto window = pybind11::cast<size_t>(value);
        if (window == 0) throw pybind11::value_error("window must be positive.");
        return window;
    }
    if (pybind11::hasattr(value, "total_seconds")) {
        const auto window = static_cast<size_t>(std::llround(
            pybind11::cast<double>(value.attr("total_seconds")()) / 60.0
        ));
        if (window == 0) throw pybind11::value_error("window must be positive.");
        return window;
    }
    throw pybind11::type_error("window must be a bar count or datetime.timedelta.");
}

pybind11::object window_as_timedelta(size_t window) {
    return pybind11::module_::import("datetime").attr("timedelta")(pybind11::arg("minutes") = window);
}

}  // namespace

void register_bollinger_bands(const pybind11::module& module) {

    // BollingerBands binding
    pybind11::class_<BollingerBands, std::shared_ptr<BollingerBands>, BaseIndicator>(module, "BollingerBands")
        .def(pybind11::init<>())
        .def(
            pybind11::init<size_t, double>(),
            pybind11::arg("window"),
            pybind11::arg("multiplier"),
            R"pbdoc(
                Construct a BollingerBands indicator.

                Parameters
                ----------
                window : int
                    Period for the simple moving average and standard deviation computation.
                multiplier : float
                    Number of standard deviations for the upper/lower bands.
            )pbdoc"
        )
        .def(
            pybind11::init([](const pybind11::object& window, double multiplier) {
                return std::make_shared<BollingerBands>(window_from_python(window), multiplier);
            }),
            pybind11::arg("window"),
            pybind11::arg("multiplier"),
            "Compatibility constructor accepting a timedelta window."
        )
        .def_property_readonly("window", [](const BollingerBands& self) {
            return window_as_timedelta(self.window);
        })
        .def_property_readonly("multiplier", [](const BollingerBands& self) {
            return self.multiplier;
        })
        .def_readwrite(
            "_cpp_window",
            &BollingerBands::window,
            R"pbdoc(
                Number of periods for the Bollinger Bands.

                Attributes
                ----------
                window : size_t
                    Window size for the Bollinger Bands.
            )pbdoc"
        )
        .def_readwrite(
            "_cpp_multiplier",
            &BollingerBands::multiplier,
            R"pbdoc(
                Multiplier for the standard deviation.

                Attributes
                ----------
                multiplier : float
                    Multiplier for the upper/lower bands.
            )pbdoc"
        )
        .def_readonly(
            "_cpp_sma",
            &BollingerBands::sma,
            R"pbdoc(
                Simple moving average values per time step.

                Attributes
                ----------
                sma : List[float]
                    Series of simple moving average values.
            )pbdoc"
        )
        .def_readonly(
            "_cpp_upper_band",
            &BollingerBands::upper_band,
            R"pbdoc(
                Upper Bollinger Band values.

                Attributes
                ----------
                upper : List[float]
                    Series of upper band values (SMA + multiplier * stddev).
            )pbdoc"
        )
        .def_readonly(
            "_cpp_lower_band",
            &BollingerBands::lower_band,
            R"pbdoc(
                Lower Bollinger Band values.

                Attributes
                ----------
                lower : List[float]
                    Series of lower band values (SMA - multiplier * stddev).
            )pbdoc"
        )
        ;


}
