#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "bollinger_bands.h"

void register_bollinger_bands(const pybind11::module& module) {

    // BollingerBands binding
    pybind11::class_<BollingerBands, std::shared_ptr<BollingerBands>, BaseIndicator>(module, "BOLLINGERBANDS")
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
