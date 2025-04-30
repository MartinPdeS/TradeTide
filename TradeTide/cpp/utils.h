#pragma once

#include <string>
#include <chrono>
#include <ctime>

#include "market/market.h"

// Helper to make a time_point from Y/M/D H:M:S in local time
TimePoint make_timepoint(int year, int month, int day, int hour, int minute, int second = 0)
{
    std::tm t{};
    t.tm_year = year - 1900;  // years since 1900
    t.tm_mon  = month  - 1;   // months since January [0..11]
    t.tm_mday = day;          // day of month [1..31]
    t.tm_hour = hour;         // hours since midnight [0..23]
    t.tm_min  = minute;       // minutes after hour [0..59]
    t.tm_sec  = second;       // seconds after minute [0..60]
    std::time_t tt = std::mktime(&t);  // interprets t as local‐time
    return std::chrono::system_clock::from_time_t(tt);
}

Market generate_market() {
    Market market("eur/cad");

    TimePoint event1 = make_timepoint(2025,  4, 30, 9,  0); // April 30, 2025 09:00
    TimePoint event2 = make_timepoint(2025, 4, 30, 9, 30); // Dec  25, 2025 09:30

    // Define a 1-minute interval:
    std::chrono::minutes one_minute{1};

    market.generate_random_market_data(event1, event2, one_minute);

    return market;
}