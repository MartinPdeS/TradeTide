#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "market.h"  // Update path as needed

PYBIND11_MODULE(interface_market, module) {
    module.doc() = "Python bindings for Market, Bid, and Ask classes used in simulation.";


    pybind11::class_<BasePrices>(module, "BasePrices")
        .def_readonly("open", &BasePrices::open)
        .def_readonly("low", &BasePrices::low)
        .def_readonly("high", &BasePrices::high)
        .def_readonly("close", &BasePrices::close)
        .def_readonly("dates", &BasePrices::dates)
    ;

    // ---------------------
    // Market Class
    // ---------------------
    pybind11::class_<Market, std::shared_ptr<Market>>(module, "Market", "Forex market data container for bid/ask prices and simulation time series.")
        .def(pybind11::init<>(), "Create an empty Market object.")

        .def(
            "load_from_csv",
            pybind11::overload_cast<const std::string&, const Duration&>(&Market::load_from_csv),
            pybind11::arg("filename"),
            pybind11::arg("time_span"),
            R"pbdoc(
                Load market data from a CSV file.

                Parameters:
                    filename (str): Path to the CSV file.
                    time_span (timedelta): Sampling interval.
                    spread_override (Optional[float]): Use fixed spread if provided.
                    is_bid_override (Optional[bool]): Override header metadata for bid/ask.
            )pbdoc"
        )

        .def("display", &Market::display_market_data, "Print a preview of the loaded market data.")

        // Read/write market metadata
        .def_readwrite("dates", &Market::dates, "Vector of datetime timestamps.")
        .def_readwrite("ask", &Market::ask, "Get open ask prices.")
        .def_readwrite("bid", &Market::bid, "Get open bid prices.")
        .def_readwrite("start_date", &Market::start_date, "Start date of the market data.")
        .def_readwrite("end_date", &Market::end_date, "End date of the market data.")
        .def_readwrite("pip_value", &Market::pip_value, "Pip value in quote currency.")

        .def(
            "add_market_data",
            &Market::add_market_data,
            pybind11::arg("timestamp"),
            pybind11::arg("ask_open"),
            pybind11::arg("ask_low"),
            pybind11::arg("ask_high"),
            pybind11::arg("ask_close"),
            pybind11::arg("bid_open"),
            pybind11::arg("bid_low"),
            pybind11::arg("bid_high"),
            pybind11::arg("bid_close"),
            R"pbdoc(
                Add a complete OHLC market data point with both ask and bid prices.

                This method adds a full market data record including open, high, low, and close prices for both ask and bid sides. The data is validated to ensure proper OHLC relationships and chronological order.

                Parameters
                ----------
                timestamp : datetime
                    The timestamp for this market data point. Must be greater than or equal to the last timestamp in the series.
                ask_open : float
                    Opening ask price for the time period.
                ask_low : float
                    Lowest ask price during the time period. Must be <= ask_open, ask_high, ask_close.
                ask_high : float
                    Highest ask price during the time period. Must be >= ask_open, ask_low, ask_close.
                ask_close : float
                    Closing ask price for the time period.
                bid_open : float
                    Opening bid price for the time period. Must be <= corresponding ask_open.
                bid_low : float
                    Lowest bid price during the time period. Must be <= bid_open, bid_high, bid_close and <= ask_low.
                bid_high : float
                    Highest bid price during the time period. Must be >= bid_open, bid_low, bid_close and <= ask_high.
                bid_close : float
                    Closing bid price for the time period. Must be <= corresponding ask_close.

                Raises
                ------
                ValueError
                    If OHLC relationships are invalid (e.g., low > high) or if bid prices exceed ask prices.
                RuntimeError
                    If the timestamp is earlier than the last timestamp in the series.

                Notes
                -----
                The method automatically updates market metadata including the number of elements, start/end dates, and time interval between data points.

                Examples
                --------
                >>> import datetime
                >>> market = Market()
                >>> timestamp = datetime.datetime(2024, 1, 1, 9, 0)
                >>> market.add_market_data(timestamp, 1.1050, 1.1040, 1.1060, 1.1055, 1.1048, 1.1038, 1.1058, 1.1053)
            )pbdoc"
        )

        .def(
            "add_tick",
            &Market::add_tick,
            pybind11::arg("timestamp"),
            pybind11::arg("ask_price"),
            pybind11::arg("bid_price"),
            R"pbdoc(
                Add a single tick data point with ask and bid prices.

                This method adds tick-level market data where the open, high, low, and close prices are all identical (representing an instantaneous price quote). The method validates the bid-ask spread and chronological order.

                Parameters
                ----------
                timestamp : datetime
                    The timestamp for this tick. Must be greater than or equal to the last timestamp in the series.
                ask_price : float
                    The ask price for this tick. Will be used for all OHLC values on the ask side.
                bid_price : float
                    The bid price for this tick. Must be <= ask_price. Will be used for all OHLC values on the bid side.

                Raises
                ------
                ValueError
                    If bid_price > ask_price (invalid spread).
                RuntimeError
                    If the timestamp is earlier than the last timestamp in the series.

                Notes
                -----
                This method is a convenience wrapper around add_market_data() where all OHLC values are identical. It's particularly useful for tick-by-tick data or when you only have bid/ask quotes without OHLC information.

                The method automatically updates market metadata including the number of elements, start/end dates, and time interval between data points.

                Examples
                --------
                >>> import datetime
                >>> market = Market()
                >>> timestamp = datetime.datetime(2024, 1, 1, 9, 0, 15)
                >>> market.add_tick(timestamp, 1.1055, 1.1053)
                >>> print(f"Market has {len(market.dates)} data points")
                Market has 1 data points
            )pbdoc"
        )
        ;
}
