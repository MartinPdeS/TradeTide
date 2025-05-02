#pragma once

#include <vector>
#include <random>
#include <chrono>
#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <iomanip>

using Duration = std::chrono::system_clock::duration;
using TimePoint = std::chrono::system_clock::time_point;

enum MarketType {
    Call,
    Bid_,
    Mean
};


class Ask {
    public:
        std::vector<double> open, close, high, low, *price;

        Ask() = default;
        Ask(
            const std::vector<double> &open,
            const std::vector<double> &close,
            const std::vector<double> &high,
            const std::vector<double> &low)
            : open(open), close(close), high(high), low(low){}
};

class Bid {
    public:
        std::vector<double> open, close, high, low, *price;

        Bid() = default;
        Bid(
            const std::vector<double> &open,
            const std::vector<double> &close,
            const std::vector<double> &high,
            const std::vector<double> &low)
            : open(open), close(close), high(high), low(low){}
};


class Market {
public:
    std::string currencies;
    TimePoint start_date;
    TimePoint end_date;
    private:
    std::vector<double> open_prices;
    std::vector<double> close_prices;
    std::vector<double> high_prices;
    std::vector<double> low_prices;
public:
    std::vector<double> spreads;
    Bid bid;
    Ask ask;

    size_t number_of_elements;

    double pip_value;
    bool is_bid;
    std::vector<TimePoint> dates;
    Duration interval;
    double current_price_per_lots;


    Market(const std::string& currencies) : currencies(currencies), is_bid(true) {}

    // Constructor for predefined data
    Market(
        const std::string currencies,
        const TimePoint start_date,
        const TimePoint end_date,
        const std::vector<double>& input_open,
        const std::vector<double>& input_close,
        const std::vector<double>& input_high,
        const std::vector<double>& input_low,
        const double pip_value
    )
        :
            currencies(currencies),
            start_date(start_date),
            end_date(end_date),
            open_prices(input_open),
            close_prices(input_close),
            high_prices(input_high),
            low_prices(input_low),
            pip_value(pip_value),
            is_bid(true)
        {
            this->number_of_elements = input_open.size();
        }


    void generate_random_market_data(const TimePoint& start_date, const TimePoint& end_date, const std::chrono::system_clock::duration& interval);

    // Display market data
    void display_market_data() const;

    std::chrono::system_clock::time_point parse_date_time(const std::string& datetime_string);

    void load_from_csv(const std::string& filename, const std::chrono::system_clock::duration& time_span);

    void set_prices(const std::string& type, bool is_bid);


};