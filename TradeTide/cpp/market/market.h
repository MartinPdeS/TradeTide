#pragma once

#include <vector>
#include <random>
#include <chrono>
#include <optional>
#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <iomanip>

using Duration = std::chrono::system_clock::duration;
using TimePoint = std::chrono::system_clock::time_point;


class BasePrices {
public:
    // Storage vectors for parsed data:
    std::vector<TimePoint> dates;
    std::vector<double> open, high, low, close;

    size_t time_idx;

    void push_back(const TimePoint &date, const double &open, const double &low, const double &high, const double &close) {
        this->dates.push_back(date);
        this->open.push_back(open);
        this->low.push_back(low);
        this->high.push_back(high);
        this->close.push_back(close);
    }
};


class Market {

public:
    BasePrices ask, bid;
    std::vector<TimePoint> dates;


    std::string currencies;
    TimePoint start_date;
    TimePoint end_date;
    size_t number_of_elements;
    double pip_value;
    Duration interval;


    Market() {}

    Duration get_duration() const {return end_date - start_date;}


    // Display market data
    void display_market_data() const;

    TimePoint parse_date_time(const std::string& datetime_string);

    /// Load market data from a CSV file.
    /// The CSV file should have a header line with named columns.
    void load_from_csv(const std::string& filename, const Duration& time_span);


    /// Figure out which column index each named field lives in.
    struct ColumnIndices {
        size_t date       = SIZE_MAX;
        size_t ask_open   = SIZE_MAX;
        size_t ask_high   = SIZE_MAX;
        size_t ask_low    = SIZE_MAX;
        size_t ask_close  = SIZE_MAX;
        size_t bid_open   = SIZE_MAX;
        size_t bid_high   = SIZE_MAX;
        size_t bid_low    = SIZE_MAX;
        size_t bid_close  = SIZE_MAX;
    };

    /// Parse the header line of a CSV file to determine the indices of each
    static ColumnIndices parse_header(const std::string& header_line);

    /// Parse a single CSV line (already split into vector<string>) according
    /// to the `cols` mapping.  Fills in all the Market data vectors.
    void parse_record(const std::vector<std::string>& fields, const ColumnIndices& cols, const TimePoint& first_ts, const Duration& time_span, double fallback_spread, std::optional<double> spread_override, bool& first_entry);

    /// Split a single CSV line by commas (no quoted-field support).
    static std::vector<std::string> split_csv_line(const std::string& line);
};