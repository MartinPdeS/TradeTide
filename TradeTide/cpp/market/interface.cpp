#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "market.h" // Replace with the actual path to your Market class header

namespace py = pybind11;
typedef std::chrono::system_clock::time_point TimePoint;

PYBIND11_MODULE(interface_market, module) {
    py::class_<Ask>(module, "Ask")
        .def_readonly("open", &Ask::open)
        .def_readonly("close", &Ask::close)
        .def_readonly("high", &Ask::high)
        .def_readonly("low", &Ask::low)
    ;

    py::class_<Bid>(module, "Bid")
        .def_readonly("open", &Bid::open)
        .def_readonly("close", &Bid::close)
        .def_readonly("high", &Bid::high)
        .def_readonly("low", &Bid::low)
    ;

    py::class_<Market>(module, "Market")
        .def(
            py::init<const std::string, const TimePoint, const TimePoint, const std::vector<double>&, const std::vector<double>&, const std::vector<double>&, const std::vector<double>&, const double>(),
            py::arg("currencies"),
            py::arg("start_date"),
            py::arg("end_date"),
            py::arg("input_open"),
            py::arg("input_close"),
            py::arg("input_high"),
            py::arg("input_low"),
            py::arg("pip_value")
        )

        // Binding the constructor for random data generation
        .def(py::init<>())

        // Binding member functions
        .def("generate_random_market_data", &Market::generate_random_market_data, py::arg("start"), py::arg("end"), py::arg("interval"))


        // Expose load_from_csv with two optional overrides
        .def("load_from_csv",
            // use the overload taking optional<double> and optional<bool>
            py::overload_cast<const std::string&, const Duration&, std::optional<double>, std::optional<bool>>(&Market::load_from_csv),
            py::arg("filename"),
            py::arg("time_span"),
            py::arg("spread_override") = std::nullopt,
            py::arg("is_bid_override") = std::nullopt,
            R"(
               load_from_csv(
                   filename: str,
                   time_span: datetime.timedelta,
                   spread_override: Optional[float] = None,
                   is_bid_override: Optional[bool] = None
               ) -> None

               Load market data from `filename` up to `time_span` from the first row.
               If `spread_override` is given, it replaces any spread in the CSV.
               If `is_bid_override` is given, it replaces the #is_bid metadata.
            )"
       )

        .def("display_market_data", &Market::display_market_data)

        .def("set_price_type", &Market::set_price, py::arg("type"))
        .def("set_is_bid", &Market::set_is_bid, py::arg("is_bid"))

        // Optionally expose the raw data vectors as read‐only properties:
        .def_readwrite("dates", &Market::dates)
        .def_readwrite("start_date", &Market::start_date)
        .def_readwrite("end_date", &Market::end_date)
        .def_readwrite("pip_value", &Market::pip_value)
        .def_readonly("ask", &Market::ask)
        .def_readonly("bid", &Market::bid)
        .def_readonly("spreads", &Market::spreads)

        ;
}
