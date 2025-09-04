#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "base_indicator/interface.cpp"
#include "moving_average_crossings/interface.cpp"
#include "bollinger_bands/interface.cpp"
#include "relative_momentum_index/interface.cpp"

namespace py = pybind11;


// This module provides Python bindings for trading indicators, including Moving Average Crossings and Bollinger Bands.
// BaseIndicator - Abstract interface for running generic indicators.
// MovingAverageCrossing - Signals based on short/long simple moving average crossovers.
// BollingerBands - Bollinger Bands calculation with buy/sell signals.
// RelativeMomentumIndex - Relative Momentum Index with overbought/oversold signals.

PYBIND11_MODULE(interface_indicators, module) {
    module.doc() = R"pbdoc(
        Python bindings for trading indicators.

        This module provides:

        - BaseIndicator: Abstract interface for running generic indicators.
        - MovingAverageCrossing: Signals based on short/long simple moving average crossovers.
        - BollingerBands: Bollinger Bands calculation with buy/sell signals.
    )pbdoc";

    register_base_indicator(module);

    register_bollinger_bands(module);

    register_moving_average_crossings(module);

    register_relative_momentum_index(module);



}
