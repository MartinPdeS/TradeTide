#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "base_indicator/base_indicator.h"
#include "moving_average_crossings/moving_average_crossings.h"
#include "bollinger_bands/bollinger_bands.h"
#include "relative_momentum_index/relative_momentum_index.h"

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
        .def(py::init<>())
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
        .def(py::init<>())
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

    // RelativeMomentumIndex binding
    py::class_<RelativeMomentumIndex, BaseIndicator>(module, "RELATIVEMOMENTUMINDEX")
        .def(py::init<>())
        .def(
            py::init<size_t, size_t, double, double>(),
            py::arg("momentum_period"),
            py::arg("smooth_period"),
            py::arg("over_bought"),
            py::arg("over_sold"),
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
        .def_readonly(
            "_cpp_signals",
            &RelativeMomentumIndex::signals,
            R"pbdoc(
                Trade signal array based on RMI thresholds.

                Attributes
                ----------
                signals : List[int]
                    +1 when crossing above over_sold (buy),
                    -1 when crossing below over_bought (sell),
                    0 otherwise.
            )pbdoc"
        );
}