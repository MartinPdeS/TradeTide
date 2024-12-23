#pragma once

#include <vector>
#include <random>
#include <chrono>
#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <iomanip>

typedef std::chrono::system_clock::time_point TimePoint;

class Market {
private:
    std::string currencies;
    std::vector<double> open_prices;
    std::vector<double> close_prices;
    std::vector<double> high_prices;
    std::vector<double> low_prices;
    std::vector<double> spreads;

    std::vector<TimePoint> dates;

public:
    TimePoint start_date;
    TimePoint end_date;

    Market(const std::string currencies) : currencies(currencies) {}

    // Constructor for predefined data
    Market(
        const std::string currencies,
        const TimePoint start_date,
        const TimePoint end_date,
        const std::vector<double>& input_open,
        const std::vector<double>& input_close,
        const std::vector<double>& input_high,
        const std::vector<double>& input_low)
        : currencies(currencies), start_date(start_date), end_date(end_date),
          open_prices(input_open), close_prices(input_close), high_prices(input_high), low_prices(input_low)
        {

        if (input_open.empty() || input_close.empty() || input_high.empty() || input_low.empty())
            std::cerr << "Error: Input arrays must not be empty.\n";

        }

    template <typename Duration>
    void generate_random_market_data(const TimePoint start_date, const TimePoint end_date) {
        // Calculate the number of days between start_date and end_date

        auto duration = std::chrono::duration_cast<Duration>(end_date - start_date).count();

        if (duration <= 0) {
            std::cerr << "Invalid date range provided.\n";
            return;
        }

        // Initialize random number generator
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<> dist_price(1.0, 100.0); // Prices between $1 and $100
        std::uniform_real_distribution<> dist_volatility(0.01, 0.05); // Daily volatility between 1% and 5%

        open_prices.clear();
        close_prices.clear();
        high_prices.clear();
        low_prices.clear();

        double prev_close = dist_price(gen); // Start with a random price

        for (int i = 0; i <= duration; ++i) {
            double open = prev_close;
            double volatility = dist_volatility(gen);
            double high = open * (1 + volatility);
            double low = open * (1 - volatility);
            double close = low + (high - low) * dist_volatility(gen);

            open_prices.push_back(open);
            close_prices.push_back(close);
            high_prices.push_back(high);
            low_prices.push_back(low);

            prev_close = close;
        }
    }

    // Getters for market data
    const std::vector<double>& get_open_prices() const { return open_prices; }
    const std::vector<double>& get_close_prices() const { return close_prices; }
    const std::vector<double>& get_high_prices() const { return high_prices; }
    const std::vector<double>& get_low_prices() const { return low_prices; }

    // Display market data
    void display_market_data() const {
        std::cout << "Market Data:\n";
        for (size_t i = 0; i < open_prices.size(); ++i) {
            std::cout << "Day " << i + 1 << ": "
                      << "Open: " << open_prices[i] << ", "
                      << "High: " << high_prices[i] << ", "
                      << "Low: " << low_prices[i] << ", "
                      << "Close: " << close_prices[i] << "\n";
        }
    }

    std::chrono::system_clock::time_point parse_date_time(const std::string& datetime_string) {
        std::tm tm = {};
        std::istringstream ss(datetime_string);
        ss >> std::get_time(&tm, "%Y-%m-%d %H:%M");
        if (ss.fail()) {
            throw std::runtime_error("Failed to parse date-time string: " + datetime_string);
        }
        return std::chrono::system_clock::from_time_t(std::mktime(&tm));
    }

    template <typename Duration>
    void load_from_csv(const std::string& filename, Duration time_span) {
        std::ifstream file(filename);
        if (!file.is_open()) {
            throw std::runtime_error("Could not open file: " + filename);
        }

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
            if (elapsed_time > time_span) {
                break;
            }

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





};