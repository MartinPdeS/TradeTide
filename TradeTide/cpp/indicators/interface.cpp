#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "base_indicator/base_indicator.h"
#include "moving_average_crossings/moving_average_crossings.h"
#include "bollinger_bands/bollinger_bands.h"

namespace py = pybind11;


// This module provides Python bindings for trading indicators, including Moving Average Crossings and Bollinger Bands.
// BaseIndicator - Abstract interface for running generic indicators.
// MovingAverageCrossing - Signals based on short/long simple moving average crossovers.
// BollingerBands - Bollinger Bands calculation with buy/sell signals.

PYBIND11_MODULE(interface_indicators, module) {
    module.doc() = R"pbdoc(
        Python bindings for trading indicators.

        This module provides:

        - BaseIndicator: Abstract interface for running generic indicators.
        - MovingAverageCrossing: Signals based on short/long simple moving average crossovers.
        - BollingerBands: Bollinger Bands calculation with buy/sell signals.
    )pbdoc";

    // BaseIndicator binding
    py::class_<BaseIndicator>(module, "BaseIndicator")
        .def(
            "_cpp_run_with_market",
            &BaseIndicator::run_with_market,
            py::arg("market"),
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
            py::arg("prices"),
            R"pbdoc(
                Run the indicator on a raw price vector.

                Parameters
                ----------
                prices : List[float]
                    Time series of price values.
            )pbdoc"
        )
        .def_readonly(
            "_cpp_signals",
            &BaseIndicator::signals,
            R"pbdoc(
                Trade signal array.

                Attributes
                ----------
                signals : List[int]
                    +1 for buy signal, -1 for sell signal, 0 otherwise.
            )pbdoc"
        )
        ;

    // MovingAverageCrossing binding
    py::class_<MovingAverageCrossing, BaseIndicator>(module, "MOVINGAVERAGECROSSING")
        .def(
            py::init<>(),
            R"pbdoc(
                Default constructor for MovingAverageCrossing.
                Initializes with default short and long window sizes.
                This constructor is primarily for internal use and should not be used directly.
            )pbdoc"
        )
        .def(
            py::init<size_t, size_t>(),
            py::arg("short_window"),
            py::arg("long_window"),
            R"pbdoc(
                Construct a MovingAverageCrossing indicator.

                Parameters
                ----------
                short_window : int
                    Window size for the short simple moving average.
                long_window : int
                    Window size for the long simple moving average.
            )pbdoc"
        )
        .def_readwrite(
            "_cpp_short_window",
            &MovingAverageCrossing::short_window,
            R"pbdoc(
                Number of periods for the short moving average.

                Attributes
                ----------
                short_window : size_t
                    Short moving average window size.
            )pbdoc"
        )
        .def_readwrite(
            "_cpp_long_window",
            &MovingAverageCrossing::long_window,
            R"pbdoc(
                Number of periods for the long moving average.

                Attributes
                ----------
                long_window : size_t
                    Long moving average window size.
            )pbdoc"
        )
        .def_readonly(
            "_cpp_short_moving_average",
            &MovingAverageCrossing::short_moving_average,
            R"pbdoc(
                Computed short simple moving average values per time step.

                Attributes
                ----------
                short_moving_average : List[float]
                    Series of short moving average values.
            )pbdoc"
        )
        .def_readonly(
            "_cpp_long_moving_average",
            &MovingAverageCrossing::long_moving_average,
            R"pbdoc(
                Computed long simple moving average values per time step.

                Attributes
                ----------
                long_moving_average : List[float]
                    Series of long moving average values.
            )pbdoc"
        )
        ;

    // BollingerBands binding
    py::class_<BollingerBands, BaseIndicator>(module, "BOLLINGERBANDS")
        .def(
            py::init<>(),
            R"pbdoc(
                Default constructor for BollingerBands.
                Initializes with default window size and multiplier.
                This constructor is primarily for internal use and should not be used directly.
            )pbdoc"
        )
        .def(
            py::init<size_t, double>(),
            py::arg("window"),
            py::arg("multiplier"),
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