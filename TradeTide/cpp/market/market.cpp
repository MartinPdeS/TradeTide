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


std::chrono::system_clock::time_point
Market::parse_date_time(const std::string& datetime_string) {
    std::tm tm = {};
    std::istringstream ss(datetime_string);
    ss >> std::get_time(&tm, "%Y-%m-%d %H:%M");
    if (ss.fail())
        throw std::runtime_error("Failed to parse date-time string: " + datetime_string);

    return std::chrono::system_clock::from_time_t(std::mktime(&tm));
}

void Market::load_from_csv(const std::string& filename, const std::chrono::system_clock::duration& time_span) {

    std::ifstream file(filename);
    if (!file.is_open())
        throw std::runtime_error("Could not open file: " + filename);

    std::string line;
    // Skip the header line
    if (!std::getline(file, line)) {
        throw std::runtime_error("File is empty or missing header: " + filename);
    }

    bool first_entry = true;
    std::chrono::system_clock::time_point start_time;

    // Read each line of the CSV
    while (std::getline(file, line)) {
        std::istringstream ss(line);
        std::string date_str, open_str, high_str, low_str, close_str, spread_str;

        // Parse each comma-separated value
        if (!std::getline(ss, date_str, ',') ||
            !std::getline(ss, open_str, ',') ||
            !std::getline(ss, high_str, ',') ||
            !std::getline(ss, low_str, ',') ||
            !std::getline(ss, close_str, ',') ||
            !std::getline(ss, spread_str, ',')) {
            throw std::runtime_error("Malformed line in CSV: " + line);
        }

        // Convert date string to time_point
        auto current_time = parse_date_time(date_str);

        // Initialize start_time with the date of the first entry
        if (first_entry) {
            start_time = current_time;
            first_entry = false;
        }

        // Calculate the elapsed time
        auto elapsed_time = current_time - start_time;

        // Stop loading if the elapsed time exceeds the specified time_span
        if (elapsed_time > time_span)
            break;

        // Convert strings to appropriate types and store
        try {
            dates.push_back(current_time);
            open_prices.push_back(std::stod(open_str));
            high_prices.push_back(std::stod(high_str));
            low_prices.push_back(std::stod(low_str));
            close_prices.push_back(std::stod(close_str));
            spreads.push_back(std::stod(spread_str));
        } catch (const std::exception& e) {
            throw std::runtime_error(std::string("Error parsing line: ") + e.what() + " Line: " + line);
        }
    }

    file.close();
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

void Market::set_prices(const std::string& type, const bool is_bid) {

    if (is_bid){
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