#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cmath>

#include "moving_average_crossings.h"

namespace {

size_t moving_average_window_from_python(const pybind11::object& value) {
    if (pybind11::isinstance<pybind11::int_>(value)) {
        const auto window = pybind11::cast<size_t>(value);
        if (window == 0) throw pybind11::value_error("Moving-average windows must be positive.");
        return window;
    }
    if (pybind11::hasattr(value, "total_seconds")) {
        const auto window = static_cast<size_t>(std::llround(
            pybind11::cast<double>(value.attr("total_seconds")()) / 60.0
        ));
        if (window == 0) throw pybind11::value_error("Moving-average windows must be positive.");
        return window;
    }
    throw pybind11::type_error(
        "Moving-average windows must be bar counts or datetime.timedelta values."
    );
}

pybind11::object moving_average_window_as_timedelta(size_t window) {
    return pybind11::module_::import("datetime").attr("timedelta")(
        pybind11::arg("minutes") = window
    );
}

}  // namespace

void register_moving_average_crossings(const pybind11::module& module) {

    // MovingAverageCrossing binding
    pybind11::class_<MovingAverageCrossing, std::shared_ptr<MovingAverageCrossing>, BaseIndicator>(module, "MovingAverageCrossing")
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
        .def(
            pybind11::init([](
                const pybind11::object& short_window,
                const pybind11::object& long_window
            ) {
                const auto short_period = moving_average_window_from_python(short_window);
                const auto long_period = moving_average_window_from_python(long_window);
                if (short_period >= long_period) {
                    throw pybind11::value_error(
                        "short_window must be smaller than long_window."
                    );
                }
                return std::make_shared<MovingAverageCrossing>(short_period, long_period);
            }),
            pybind11::arg("short_window"),
            pybind11::arg("long_window"),
            "Compatibility constructor accepting timedelta windows."
        )
        .def_property_readonly("short_window", [](const MovingAverageCrossing& self) {
            return moving_average_window_as_timedelta(self.short_window);
        })
        .def_property_readonly("long_window", [](const MovingAverageCrossing& self) {
            return moving_average_window_as_timedelta(self.long_window);
        })
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
