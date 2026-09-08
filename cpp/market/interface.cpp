#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include <pybind11/stl/filesystem.h>
#include <algorithm>
#include <cctype>
#include <regex>
#include "market.h"  // Update path as needed

namespace py = pybind11;

namespace {
Duration parse_time_span(const py::object& value) {
    if (!py::isinstance<py::str>(value)) {
        Duration duration;
        try {
            duration = value.cast<Duration>();
        } catch (const py::cast_error&) {
            throw py::type_error("time_span must be a datetime.timedelta or a duration string.");
        }
        if (duration <= Duration::zero()) {
            throw py::value_error("time_span must be greater than zero.");
        }
        return duration;
    }
    const std::string text = value.cast<std::string>();
    std::regex token(R"((\d+)\s*(d(?:ays?)?|h(?:ours?)?|m(?:inutes?)?|s(?:econds?)?))", std::regex::icase);
    Duration total{};
    std::sregex_iterator current(text.begin(), text.end(), token), end;
    std::string remainder = std::regex_replace(text, token, "");
    remainder.erase(std::remove_if(remainder.begin(), remainder.end(), ::isspace), remainder.end());
    if (current == end || !remainder.empty()) {
        throw py::value_error("time_span must be a positive duration such as '2d 6h' or '90m'.");
    }
    for (; current != end; ++current) {
        const auto amount = std::stoll((*current)[1].str());
        std::string unit = (*current)[2].str();
        std::transform(unit.begin(), unit.end(), unit.begin(), ::tolower);
        if (unit[0] == 'd') total += std::chrono::hours(24 * amount);
        else if (unit[0] == 'h') total += std::chrono::hours(amount);
        else if (unit[0] == 'm') total += std::chrono::minutes(amount);
        else total += std::chrono::seconds(amount);
    }
    if (total <= Duration::zero()) throw py::value_error("time_span must be greater than zero.");
    return total;
}

std::string currency_code(const py::object& currency, const char* parameter) {
    if (!py::hasattr(currency, "value")) {
        throw py::type_error(std::string(parameter) + " must be a Currency member.");
    }
    return py::str(currency.attr("value"));
}

py::object plot_candles(Market& market, py::object axes, const std::string& side, std::optional<size_t> max_candles, bool show) {
    if (side != "ask" && side != "bid") throw py::value_error("side must be either 'ask' or 'bid'.");
    const BasePrices& prices = side == "ask" ? market.ask : market.bid;
    if (prices.open.empty()) throw py::value_error("Market has no observations to plot.");
    if (max_candles && *max_candles == 0) throw py::value_error("max_candles must be a positive integer or None.");
    const size_t count = prices.open.size();
    const size_t target = max_candles ? std::min(*max_candles, count) : count;
    const size_t group_size = (count + target - 1) / target;
    py::list dates, segments, bodies, colors;
    const auto dates_to_num = py::module_::import("matplotlib.dates").attr("date2num");
    for (size_t start = 0; start < count; start += group_size) {
        const size_t end = std::min(start + group_size, count);
        double low = prices.low[start], high = prices.high[start];
        for (size_t index = start + 1; index < end; ++index) { low = std::min(low, prices.low[index]); high = std::max(high, prices.high[index]); }
        dates.append(py::cast(market.dates[start]));
        const double open = prices.open[start], close = prices.close[end - 1];
        const double x = dates_to_num(py::cast(market.dates[start])).cast<double>();
        segments.append(py::make_tuple(py::make_tuple(x, low), py::make_tuple(x, high)));
        const std::string color = close >= open ? "#16a085" : "#e74c3c";
        colors.append(color);
        bodies.append(py::make_tuple(py::make_tuple(x - 0.0002, open), py::make_tuple(x + 0.0002, open), py::make_tuple(x + 0.0002, close), py::make_tuple(x - 0.0002, close)));
    }
    py::object figure;
    if (axes.is_none()) {
        const py::tuple created = py::module_::import("matplotlib.pyplot").attr("subplots")().cast<py::tuple>();
        figure = created[0]; axes = created[1];
    } else figure = axes.attr("figure");
    const auto collections = py::module_::import("matplotlib.collections");
    axes.attr("add_collection")(collections.attr("LineCollection")(segments, py::arg("colors") = colors, py::arg("linewidths") = 0.8));
    axes.attr("add_collection")(collections.attr("PolyCollection")(bodies, py::arg("facecolors") = colors, py::arg("edgecolors") = colors, py::arg("linewidths") = 0.5));
    axes.attr("autoscale_view")();
    axes.attr("set_xlabel")("Time"); axes.attr("set_ylabel")("Price");
    axes.attr("set_title")(market.currency_pair + " - candles");
    figure.attr("tight_layout")();
    if (show) py::module_::import("matplotlib.pyplot").attr("show")();
    return figure;
}
}

PYBIND11_MODULE(market, module) {
    module.doc() = R"pbdoc(
        Native market-data containers for TradeTide.

        ``Market`` stores synchronised bid/ask OHLC observations and is the
        input to indicators, signals, positions, and backtests.
    )pbdoc";


    py::class_<BasePrices>(module, "BasePrices")
        .def_readonly("open", &BasePrices::open)
        .def_readonly("low", &BasePrices::low)
        .def_readonly("high", &BasePrices::high)
        .def_readonly("close", &BasePrices::close)
        .def_readonly("dates", &BasePrices::dates)
        .def("__repr__", [](const BasePrices& self) {
            return "<BasePrices observations=" + std::to_string(self.close.size()) + ">";
        })
    ;

    // ---------------------
    // Market Class
    // ---------------------
    py::class_<Market, std::shared_ptr<Market>>(module, "Market", "Forex market data container for bid/ask prices and simulation time series.")
        .def(py::init<>(), "Create an empty Market object.")

        .def(
            "load_from_csv",
            py::overload_cast<const std::string&, const Duration&>(&Market::load_from_csv),
            py::arg("filename"), py::arg("time_span"),
            R"pbdoc(
                Load market data from a CSV file.

                Parameters:
                    filename (str): Path to the CSV file.
                    time_span (timedelta): Sampling interval.
                    spread_override (Optional[float]): Use fixed spread if provided.
                    is_bid_override (Optional[bool]): Override header metadata for bid/ask.
            )pbdoc"
        )
        .def("load_from_database", [](Market& self, py::object currency_0, py::object currency_1, py::object time_span) {
            const std::string base = currency_code(currency_0, "currency_0");
            const std::string quote = currency_code(currency_1, "currency_1");
            if (base == quote) throw py::value_error("currency_0 and currency_1 must be different currencies.");
            self.time_span = parse_time_span(time_span);
            self.currency_pair = base + "/" + quote;
            const auto data = py::module_::import("TradeTide.directories").attr("data");
            const std::filesystem::path path = py::str(data).cast<std::string>();
            const auto file = path / (base + "_" + quote + ".csv");
            if (!std::filesystem::is_regular_file(file)) {
                std::vector<std::string> available;
                for (const auto& entry : std::filesystem::directory_iterator(path)) {
                    if (entry.path().extension() == ".csv") available.push_back(entry.path().stem().string());
                }
                std::sort(available.begin(), available.end());
                std::ostringstream message;
                message << "No bundled market data is available for " << self.currency_pair << ". Available datasets: ";
                for (size_t index = 0; index < available.size(); ++index) {
                    if (index) message << ", ";
                    message << available[index];
                }
                PyErr_SetString(PyExc_FileNotFoundError, message.str().c_str());
                throw py::error_already_set();
            }
            self.load_from_csv(file.string(), self.time_span);
        }, py::arg("currency_0"), py::arg("currency_1"), py::arg("time_span"), "Load bundled market data for a Currency pair.")
        .def_static("_parse_timespan", &parse_time_span, py::arg("time_span"), "Parse a timedelta or compact duration string.")
        .def("plot_candles", [](Market& self, py::object axes, const std::string& side, std::optional<size_t> max_candles, bool show) { return plot_candles(self, axes, side, max_candles, show); }, py::arg("axes") = py::none(), py::arg("side") = "ask", py::arg("max_candles") = 2000, py::arg("show") = true, "Render batched native-market candles.")

        .def("display", &Market::display_market_data, "Print a preview of the loaded market data.")
        .def("__repr__", [](const Market& self) {
            return "<Market observations=" + std::to_string(self.dates.size()) + ">";
        })

        // Read/write market metadata
        .def_readwrite("dates", &Market::dates, "Vector of datetime timestamps.")
        .def_readwrite("ask", &Market::ask, "Get open ask prices.")
        .def_readwrite("bid", &Market::bid, "Get open bid prices.")
        .def_readwrite("start_date", &Market::start_date, "Start date of the market data.")
        .def_readwrite("end_date", &Market::end_date, "End date of the market data.")
        .def_readwrite("pip_value", &Market::pip_value, "Pip value in quote currency.")
        .def_readwrite("currency_pair", &Market::currency_pair)
        .def_readwrite("time_span", &Market::time_span)

        .def(
            "add_market_data",
            &Market::add_market_data,
            pybind11::arg("timestamp"),
            pybind11::arg("ask_open"),
            pybind11::arg("ask_high"),
            pybind11::arg("ask_low"),
            pybind11::arg("ask_close"),
            pybind11::arg("bid_open"),
            pybind11::arg("bid_high"),
            pybind11::arg("bid_low"),
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
