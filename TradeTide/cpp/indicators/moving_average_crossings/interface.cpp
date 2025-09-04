#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "moving_average_crossings.h"

void register_moving_average_crossings(const pybind11::module& module) {

    // MovingAverageCrossing binding
    pybind11::class_<MovingAverageCrossing, std::shared_ptr<MovingAverageCrossing>, BaseIndicator>(module, "MOVINGAVERAGECROSSING")
        .def(pybind11::init<>())
        .def(
            pybind11::init<size_t, size_t>(),
            pybind11::arg("short_window"),
            pybind11::arg("long_window"),
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


}
