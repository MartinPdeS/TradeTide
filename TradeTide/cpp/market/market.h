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


class Ask {
    public:
        std::vector<double> open, close, high, low, *price;

        [[nodiscard]] const std::vector<double>& get_price(){return *this->price;}

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

        [[nodiscard]] const std::vector<double>& get_price(){return *this->price;}

        Bid() = default;
        Bid(
            const std::vector<double> &open,
            const std::vector<double> &close,
            const std::vector<double> &high,
            const std::vector<double> &low)
            : open(open), close(close), high(high), low(low){}
};


class Market {
private:
    std::vector<double> open_prices;
    std::vector<double> close_prices;
    std::vector<double> high_prices;
    std::vector<double> low_prices;
public:
    std::string currencies;
    TimePoint start_date;
    TimePoint end_date;
    std::vector<double> spreads;
    std::vector<double> volumes;
    Bid bid;
    Ask ask;
    size_t number_of_elements;
    double pip_value;
    bool is_bid;
    std::vector<TimePoint> dates;
    Duration interval;


    Market() : is_bid(true) {}

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
            open_prices(input_open),
            close_prices(input_close),
            high_prices(input_high),
            low_prices(input_low),
            currencies(currencies),
            start_date(start_date),
            end_date(end_date),
            pip_value(pip_value),
            is_bid(true)
        {
            this->number_of_elements = input_open.size();
        }

    Duration get_duration() const {
        return end_date - start_date;
    }


    void generate_random_market_data(const TimePoint& start_date, const TimePoint& end_date, const std::chrono::system_clock::duration& interval);

    // Display market data
    void display_market_data() const;

    TimePoint parse_date_time(const std::string& datetime_string);

    /// If `spread_override` has a value, ALWAYS use that value
    /// instead of any “spread” column in the CSV.
    /// If `is_bid_override` has a value, ALWAYS use that value
    /// instead of any `#is_bid=` metadata.
    void load_from_csv(const std::string& filename, const Duration& time_span, std::optional<double> spread_override = std::nullopt, std::optional<bool> is_bid_override = std::nullopt);


    /// Figure out which column index each named field lives in.
    struct ColumnIndices {
        size_t date   = SIZE_MAX;
        size_t open   = SIZE_MAX;
        size_t high   = SIZE_MAX;
        size_t low    = SIZE_MAX;
        size_t close  = SIZE_MAX;
        size_t volume = SIZE_MAX;  // optional
        size_t spread = SIZE_MAX;  // optional
    };

    static ColumnIndices parse_header(const std::string& header_line);

    /// Parse a single CSV line (already split into vector<string>) according
    /// to the `cols` mapping.  Fills in all the Market data vectors.
    void parse_record(const std::vector<std::string>& fields, const ColumnIndices& cols, const TimePoint& first_ts, const Duration& time_span, double fallback_spread, std::optional<double> spread_override, bool& first_entry);

    /// Split a single CSV line by commas (no quoted-field support).
    static std::vector<std::string> split_csv_line(const std::string& line);

    void set_is_bid(const bool is_bid);
    void set_price(const std::string& type);
};