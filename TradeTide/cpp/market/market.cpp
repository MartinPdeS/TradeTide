#include "market.h"

// Display market data with tabs between fields
void
Market::display_market_data() const {
    std::cout << "Market Data:\n";

    for (size_t i = 0; i < ask.open.size(); ++i) {
        std::time_t t = std::chrono::system_clock::to_time_t(dates[i]);

        std::cout
            << "Iteration "  << i                        << "\t\t"
            // << "Date: "      << dates[i]                 << "\t\t"
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




    // Loads CSV and stops when time_span is exceeded, requiring pip_value metadata
void Market::load_from_csv(const std::string& filename, const std::chrono::system_clock::duration& time_span) {
    std::ifstream file(filename);
    if (!file.is_open())
        throw std::runtime_error("Cannot open file: " + filename);

    std::string line;
    std::string header_line;
    bool pip_found = false;
    static const std::string key = "pip_value=";

    // Read metadata lines (starting with '#') to pick up mandatory pip_value
    while (std::getline(file, line)) {
        if (line.empty())
            continue;
        if (line[0] == '#') {
            auto meta = line.substr(1);
            if (meta.rfind(key, 0) == 0) {
                pip_value = std::stod(meta.substr(key.size()));
                pip_found = true;
            }
            continue;
        }
        header_line = line;
        break;
    }
    if (!pip_found) {
        throw std::runtime_error("Missing mandatory metadata: pip_value");
    }
    if (header_line.empty())
        throw std::runtime_error("Missing CSV header in: " + filename);

    ColumnIndices cols = parse_header(header_line);

    bool first_entry = true;
    auto first_tp = std::chrono::system_clock::time_point();

    // Read data rows
    while (std::getline(file, line)) {
        if (line.empty()) continue;
        auto fields = split_csv_line(line);

        // Parse date/time
        TimePoint time_point = parse_date_time(fields[cols.date]);

        // Enforce time span
        if (first_entry) {
            first_tp = time_point;
            first_entry = false;
        } else if (time_point - first_tp > time_span) {
            break;
        }

        // Store timestamp
        this->dates.push_back(time_point);

        this->ask.push_back(
            time_point,
            std::stod(fields[cols.ask_open]),
            std::stod(fields[cols.ask_low]),
            std::stod(fields[cols.ask_high]),
            std::stod(fields[cols.ask_close])
        );


        // Store timestamp
        this->bid.push_back(
            time_point,
            std::stod(fields[cols.bid_open]),
            std::stod(fields[cols.bid_low]),
            std::stod(fields[cols.bid_high]),
            std::stod(fields[cols.bid_close])
        );
    }
};