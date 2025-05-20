#include "market.h"

void
Market::generate_random_market_data(const TimePoint& start_date, const TimePoint& end_date, const std::chrono::system_clock::duration& interval)
{
    if (start_date >= end_date) {
        std::cerr << "Invalid date range provided.\n";
        return;
    }

    this->pip_value = 0.0001;
    this->interval = interval;

    // Initialize random number generator
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dist_price(1.0, 100.0);      // Prices between $1 and $100
    std::uniform_real_distribution<> dist_volatility(0.01, 0.05); // Volatility between 1% and 5%
    std::uniform_real_distribution<> dist_spread(0.001, 0.005);   // Spread between 0.1% and 0.5% of the price

    // Clear previous data
    open_prices.clear();
    close_prices.clear();
    high_prices.clear();
    low_prices.clear();
    dates.clear();
    spreads.clear();

    double prev_close = dist_price(gen); // Start with a random price

    for (TimePoint current_time = start_date; current_time <= end_date; current_time += interval) {
        double open       = prev_close;
        double volatility = dist_volatility(gen);
        double high       = open * (1 + volatility);
        double low        = open * (1 - volatility);
        double close      = low + (high - low) * dist_volatility(gen);

        // Compute a small random spread around the mid-price
        double mid_price = (high + low) / 2.0;
        double spread    = mid_price * dist_spread(gen);

        open_prices.push_back(open);
        high_prices.push_back(high);
        low_prices.push_back(low);
        close_prices.push_back(close);
        spreads.push_back(spread);
        dates.push_back(current_time);

        prev_close = close;
    }

    this->number_of_elements = close_prices.size();
}



// Display market data with tabs between fields
void
Market::display_market_data() const {
    std::cout << "Market Data:\n";
    for (size_t i = 0; i < open_prices.size(); ++i) {
        std::cout
            << "Day "    << (i + 1)                     << '\t'
            << "Open: "  << open_prices[i]              << '\t'
            << "High: "  << high_prices[i]              << '\t'
            << "Low: "   << low_prices[i]               << '\t'
            << "Close: " << close_prices[i]             << '\t'
            << "Spread: "<< spreads[i]                  << '\n';
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

void Market::set_is_bid(const bool is_bid) {
    this->is_bid = is_bid;

    if (this->is_bid){
        this->bid = Bid(
            this->open_prices,
            this->close_prices,
            this->high_prices,
            this->low_prices
        );

        this->ask = Ask(
            add_value(this->open_prices, this->spreads),
            add_value(this->close_prices, this->spreads),
            add_value(this->high_prices, this->spreads),
            add_value(this->low_prices, this->spreads)
        );
    }

    else {
        this->ask = Ask(
            this->open_prices,
            this->close_prices,
            this->high_prices,
            this->low_prices
        );

        this->bid = Bid(
            substract_value(this->open_prices, this->spreads),
            substract_value(this->close_prices, this->spreads),
            substract_value(this->high_prices, this->spreads),
            substract_value(this->low_prices, this->spreads)
        );
    }


}

void Market::set_price(const std::string& type) {

    // Set the prices based on the type (open/close/high/low)
    if (type == "open") {
        this->ask.price = &this->ask.open;
        this->bid.price = &this->bid.open;
    } else if (type == "close") {
        this->ask.price = &this->ask.close;
        this->bid.price = &this->bid.close;
    } else if (type == "high") {
        this->ask.price = &this->ask.high;
        this->bid.price = &this->bid.high;
    } else if (type == "low") {
        this->ask.price = &this->ask.low;
        this->bid.price = &this->bid.low;
    } else {
        throw std::invalid_argument("Invalid price type: must be 'open', 'close', 'high', or 'low'");
    }
}

TimePoint Market::parse_date_time(const std::string& s) {
    std::tm tm = {};
    std::istringstream ss(s);
    ss >> std::get_time(&tm, "%Y-%m-%d %H:%M");
    if (ss.fail()) {
        throw std::runtime_error("Invalid date format: " + s);
    }
    return std::chrono::system_clock::from_time_t(std::mktime(&tm));
}

Market::ColumnIndices Market::parse_header(const std::string& header_line) {
    ColumnIndices idx;
    std::istringstream ss(header_line);
    std::string col;
    size_t i = 0;
    while (std::getline(ss, col, ',')) {
        if      (col == "date")   idx.date   = i;
        else if (col == "open")   idx.open   = i;
        else if (col == "high")   idx.high   = i;
        else if (col == "low")    idx.low    = i;
        else if (col == "close")  idx.close  = i;
        else if (col == "volume") idx.volume = i;
        else if (col == "spread") idx.spread = i;
        ++i;
    }
    // sanity check
    if (idx.date   == SIZE_MAX ||
        idx.open   == SIZE_MAX ||
        idx.high   == SIZE_MAX ||
        idx.low    == SIZE_MAX ||
        idx.close  == SIZE_MAX)
    {
        throw std::runtime_error("Header missing required columns");
    }
    return idx;
}

std::vector<std::string>
Market::split_csv_line(const std::string& line) {
    std::vector<std::string> out;
    std::istringstream ss(line);
    std::string field;
    while (std::getline(ss, field, ',')) {
        out.push_back(field);
    }
    return out;
}




void Market::load_from_csv(
    const std::string& filename,
    const Duration& time_span,
    std::optional<double> spread_override,
    std::optional<bool> is_bid_override)
{
    std::ifstream file(filename);
    if (!file.is_open())
        throw std::runtime_error("Cannot open file: " + filename);

    std::string line, header_line;

    // 1) Metadata block: scan leading '#' lines for is_bid= and pip_size=
    //
    //    If the user did *not* override is_bid/is_bid_override, we pick up
    //    an in-file "#is_bid=true" or "#is_bid=false".  Likewise for pip_size.
    //
    while (std::getline(file, line)) {
        if (line.empty())
            continue;

        if (line[0] == '#') {
            auto meta = line.substr(1);  // strip leading '#'

            // pip_size=…  → set Market::pip_size if not overridden by code
            if (meta.rfind("pip_size=", 0) == 0) {
                auto val = meta.substr(std::string{"pip_size="}.size());
                this->pip_value = std::stod(val);
            }

            // is_bid=…   → set Market::is_bid if user did not pass is_bid_override
            if (!is_bid_override && meta.rfind("is_bid=", 0) == 0) {
                auto val = meta.substr(std::string{"is_bid="}.size());
                is_bid = (val == "1" || val == "true" || val == "True");
            }

            continue;  // keep consuming '#' lines
        }

        // first non-# line must be our CSV header
        header_line = line;
        break;
    }

    if (header_line.empty())
        throw std::runtime_error("Missing CSV header in: " + filename);

    // 2) Figure out column layout
    ColumnIndices cols = parse_header(header_line);

    // 3) Read & parse each data row
    bool first_entry = true;
    while (std::getline(file, line)) {
        if (line.empty())
            continue;

        auto fields = split_csv_line(line);
        try {
            parse_record(
                fields,
                cols,
                /*first_ts=*/ dates.empty() ? TimePoint{} : dates.front(),
                time_span,
                /*fallback_spread=*/ spread_override.value_or(0.0),
                spread_override,
                first_entry
            );
        }
        catch (const std::out_of_range&) {
            // time_span exceeded → stop loading
            break;
        }
        catch (const std::exception& e) {
            throw std::runtime_error("Error parsing line: " + std::string{e.what()});
        }
    }

    // 4) Apply the final is_bid setting via your setter:
    if (is_bid_override) {
        // caller wins
        set_is_bid(*is_bid_override);
    } else {
        // file-derived metadata wins
        set_is_bid(is_bid);
    }
}


void Market::parse_record(
    const std::vector<std::string>& fields,
    const ColumnIndices& cols,
    const TimePoint& first_ts,
    const Duration& time_span,
    double fallback_spread,
    std::optional<double> spread_override,
    bool& first_entry)
{
    // 1) parse timestamp
    TimePoint t = parse_date_time(fields[cols.date]);

    // 2) push it (and enforce time_span)
    if (first_entry) {
        first_entry = false;
        dates.push_back(t);
    } else {
        if (t - first_ts > time_span) {
            throw std::out_of_range("time_span exceeded");
        }
        dates.push_back(t);
    }

    // 3) parse prices
    open_prices .push_back(std::stod(fields[cols.open]));
    high_prices .push_back(std::stod(fields[cols.high]));
    low_prices  .push_back(std::stod(fields[cols.low]));
    close_prices.push_back(std::stod(fields[cols.close]));

    if (cols.volume != SIZE_MAX)
        volumes.push_back(std::stod(fields[cols.volume]));

    // 4) spread logic
    if (spread_override) {
        spreads.push_back(*spread_override);
    }
    else if (cols.spread != SIZE_MAX) {
        spreads.push_back(std::stod(fields[cols.spread]));
    }
    else {
        spreads.push_back(fallback_spread);
    }
}

