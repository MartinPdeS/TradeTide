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
public:
    std::string currencies;
    TimePoint start_date;
    TimePoint end_date;
    std::vector<double> open_prices;
    std::vector<double> close_prices;
    std::vector<double> high_prices;
    std::vector<double> low_prices;
    std::vector<double> spreads;

    std::vector<TimePoint> dates;
    TimePoint interval;




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
    void generate_random_market_data(const TimePoint& start_date, const TimePoint& end_date, const Duration& interval);

    // Getters for market data
    const std::vector<double>& get_open_prices() const { return open_prices; }
    const std::vector<double>& get_close_prices() const { return close_prices; }
    const std::vector<double>& get_high_prices() const { return high_prices; }
    const std::vector<double>& get_low_prices() const { return low_prices; }

    // Display market data
    void display_market_data() const;

    std::chrono::system_clock::time_point parse_date_time(const std::string& datetime_string);

    template <typename Duration>
    void load_from_csv(const std::string& filename, const Duration &time_span);



};