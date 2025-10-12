#include "market.h"

// Display market data with tabs between fields
void
Market::display_market_data() const {
    std::cout << "Market Data:\n";

    for (size_t i = 0; i < ask.open.size(); ++i) {
        std::time_t t = std::chrono::system_clock::to_time_t(dates[i]);

        std::cout
            << "Iteration "  << i                        << "\t\t"
            << "Date: "      << std::put_time(std::localtime(&t), "%Y-%m-%d %H:%M") << "\t\t"
            << "Ask-Open: "  << ask.open[i]              << "\t\t"
            << "Ask-High: "  << ask.high[i]              << "\t\t"
            << "Ask-Low: "   << ask.low[i]               << "\t\t"
            << "Ask-Close: " << ask.close[i]             << "\t\t"
            << "Bid-Open: "  << bid.open[i]              << "\t\t"
            << "Bid-High: "  << bid.high[i]              << "\t\t"
            << "Bid-Low: "   << bid.low[i]               << "\t\t"
            << "Bid-Close: " << bid.close[i]             << "\n"
            ;
    }
}

std::vector<double> add_value(const std::vector<double>& vector, const std::vector<double> &spread){
    std::vector<double> output;
    output.reserve(vector.size());

    for (size_t idx = 0; idx < vector.size(); idx++)
        output.push_back(vector[idx] + 1e-4 * spread[idx]);

    return output;
}

std::vector<double> substract_value(const std::vector<double>& vector, const std::vector<double> &spread){
    std::vector<double> output;
    output.reserve(vector.size());

    for (size_t idx = 0; idx < vector.size(); idx++)
        output.push_back(vector[idx] - 1e-4 * spread[idx]);

    return output;
}

TimePoint Market::parse_date_time(const std::string& s) {
    std::tm tm = {};
    std::istringstream ss(s);
    ss >> std::get_time(&tm, "%Y-%m-%d %H:%M");
    if (ss.fail()) {
        throw std::runtime_error("Invalid date format: " + s);
    }
    auto time = std::mktime(&tm);
    return TimePoint{std::chrono::system_clock::from_time_t(time)};
}

Market::ColumnIndices Market::parse_header(const std::string& header_line) {
    Market::ColumnIndices idx;
    std::istringstream ss(header_line);
    std::string col;
    size_t i = 0;
    while (std::getline(ss, col, ',')) {
        if      (col == "date")      idx.date      = i;
        else if (col == "ask_open")  idx.ask_open  = i;
        else if (col == "ask_high")  idx.ask_high  = i;
        else if (col == "ask_low")   idx.ask_low   = i;
        else if (col == "ask_close") idx.ask_close = i;
        else if (col == "bid_open")  idx.bid_open  = i;
        else if (col == "bid_high")  idx.bid_high  = i;
        else if (col == "bid_low")   idx.bid_low   = i;
        else if (col == "bid_close") idx.bid_close = i;
        ++i;
    }
    // sanity check
    if (idx.date == SIZE_MAX ||
        idx.ask_open == SIZE_MAX || idx.ask_high == SIZE_MAX ||
        idx.ask_low  == SIZE_MAX || idx.ask_close == SIZE_MAX ||
        idx.bid_open == SIZE_MAX || idx.bid_high  == SIZE_MAX ||
        idx.bid_low  == SIZE_MAX || idx.bid_close == SIZE_MAX) {
        throw std::runtime_error("Header missing required columns");
    }
    return idx;
}

std::vector<std::string> Market::split_csv_line(const std::string& line) {
    std::vector<std::string> out;
    std::istringstream ss(line);
    std::string field;
    while (std::getline(ss, field, ',')) {
        out.push_back(field);
    }
    return out;
}




// Loads a CSV file into the Market object.
// The CSV must contain ASK and BID OHLC data and a metadata line specifying pip_value.
// Parsing stops once the specified time_span is exceeded.
void Market::load_from_csv(
    const std::string& filename,
    const std::chrono::system_clock::duration& time_span
) {
    if (time_span <= std::chrono::system_clock::duration::zero()) {
        throw std::invalid_argument("Time span must be positive");
    }

    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open file: " + filename);
    }

    constexpr std::string_view pip_key = "pip_value=";
    bool pip_found = false;
    std::string line;
    std::string header_line;

    // ─────────────────────────────────────────────
    // 1. Parse metadata header (lines starting with '#')
    // ─────────────────────────────────────────────
    while (std::getline(file, line)) {
        if (line.empty()) continue;

        if (line[0] == '#') {
            const std::string meta = line.substr(1);
            if (meta.rfind(pip_key, 0) == 0) {
                pip_value = std::stod(meta.substr(pip_key.size()));
                pip_found = true;
            }
            continue; // keep reading until we reach the CSV header
        }

        // first non-# line → header
        header_line = line;
        break;
    }

    if (!pip_found) {
        std::ostringstream msg;
        msg << "Missing mandatory metadata: pip_value\n\n"
            << "Expected header example:\n\n"
            << "#METADATA:\n"
            << "#pip_value=0.0001\n"
            << "#DATA\n"
            << "date,ask_open,ask_high,ask_low,ask_close,bid_open,bid_high,bid_low,bid_close\n"
            << "2023-08-08 03:56:00,1.33937,1.33948,1.33937,1.33948,1.33937,1.33948,1.33937,1.33948\n"
            << "2023-08-08 03:57:00,1.33947,1.33949,1.33934,1.33935,1.33947,1.33949,1.33934,1.33935\n";
        throw std::runtime_error(msg.str());
    }

    if (header_line.empty())
        throw std::runtime_error("Missing CSV header in: " + filename);

    // ─────────────────────────────────────────────
    // 2. Parse header and validate required columns
    // ─────────────────────────────────────────────
    ColumnIndices cols = parse_header(header_line);

    const bool has_ask = cols.ask_open  >= 0 && cols.ask_high  >= 0 &&
                         cols.ask_low   >= 0 && cols.ask_close >= 0;

    const bool has_bid = cols.bid_open  >= 0 && cols.bid_high  >= 0 &&
                         cols.bid_low   >= 0 && cols.bid_close >= 0;

    if (!has_ask || !has_bid) {
        throw std::runtime_error("CSV file must contain complete ASK and BID OHLC columns");
    }

    // ─────────────────────────────────────────────
    // 3. Parse data rows
    // ─────────────────────────────────────────────
    bool first_entry = true;
    TimePoint first_time_point{};

    while (std::getline(file, line)) {
        if (line.empty()) continue;

        const auto fields = split_csv_line(line);

        // Parse timestamp
        const TimePoint current_time = parse_date_time(fields[cols.date]);

        // Stop when time_span exceeded
        if (first_entry) {
            first_time_point = current_time;
            first_entry = false;
        } else if (current_time - first_time_point > time_span) {
            break;
        }

        // Save timestamp
        dates.push_back(current_time);

        // ASK data
        ask.push_back(
            current_time,
            std::stod(fields[cols.ask_open]),
            std::stod(fields[cols.ask_low]),
            std::stod(fields[cols.ask_high]),
            std::stod(fields[cols.ask_close])
        );

        // BID data
        bid.push_back(
            current_time,
            std::stod(fields[cols.bid_open]),
            std::stod(fields[cols.bid_low]),
            std::stod(fields[cols.bid_high]),
            std::stod(fields[cols.bid_close])
        );
    }

    if (dates.empty()) {
        throw std::runtime_error("No valid data rows found in: " + filename);
    }
}


void Market::add_market_data(const TimePoint& timestamp, double ask_open, double ask_high, double ask_low, double ask_close, double bid_open, double bid_high, double bid_low, double bid_close) {
    // Validate OHLC relationships for ask prices
    if (ask_low > ask_open || ask_low > ask_close || ask_low > ask_high) {
        throw std::invalid_argument("Ask low price cannot be greater than open, close, or high prices");
    }
    if (ask_high < ask_open || ask_high < ask_close || ask_high < ask_low) {
        throw std::invalid_argument("Ask high price cannot be less than open, close, or low prices");
    }

    // Validate OHLC relationships for bid prices
    if (bid_low > bid_open || bid_low > bid_close || bid_low > bid_high) {
        throw std::invalid_argument("Bid low price cannot be greater than open, close, or high prices");
    }
    if (bid_high < bid_open || bid_high < bid_close || bid_high < bid_low) {
        throw std::invalid_argument("Bid high price cannot be less than open, close, or low prices");
    }

    // Validate bid-ask spread (bid should be <= ask for all prices)
    if (bid_open > ask_open || bid_high > ask_high || bid_low > ask_low || bid_close > ask_close) {
        throw std::invalid_argument("Bid prices cannot be greater than corresponding ask prices");
    }

    // Validate chronological order
    if (!dates.empty() && timestamp < dates.back()) {
        throw std::logic_error("New timestamp must be greater than or equal to the last timestamp");
    }

    // Add data to the respective containers
    ask.push_back(timestamp, ask_open, ask_low, ask_high, ask_close);
    bid.push_back(timestamp, bid_open, bid_low, bid_high, bid_close);
    dates.push_back(timestamp);

    // Update market metadata
    number_of_elements = dates.size();
    if (dates.size() == 1) {
        start_date = timestamp;
    }
    end_date = timestamp;

    // Calculate interval if we have at least 2 data points
    if (dates.size() >= 2) {
        interval = dates.back() - dates[dates.size() - 2];
    }
}

void Market::add_tick(const TimePoint& timestamp, double ask_price, double bid_price) {
    // Validate bid-ask spread
    if (bid_price > ask_price) {
        throw std::invalid_argument("Bid price cannot be greater than ask price");
    }

    // Validate chronological order
    if (!dates.empty() && timestamp < dates.back()) {
        throw std::logic_error("New timestamp must be greater than or equal to the last timestamp");
    }

    // Use the same price for all OHLC values (tick data)
    add_market_data(timestamp, ask_price, ask_price, ask_price, ask_price, bid_price, bid_price, bid_price, bid_price);
}
