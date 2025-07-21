/**
 * @file market.h
 * @brief Market data management and CSV parsing for trading simulations
 *
 * This file contains classes for loading, storing, and managing financial market data.
 * It provides functionality for parsing CSV files containing OHLC (Open, High, Low, Close)
 * price data for both bid and ask prices, essential for realistic trading simulations.
 */

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

/// Type alias for system clock duration representation
using Duration = std::chrono::system_clock::duration;
/// Type alias for system clock time point representation
using TimePoint = std::chrono::system_clock::time_point;


/**
 * @class BasePrices
 * @brief Container for OHLC (Open, High, Low, Close) price data with timestamps
 *
 * The BasePrices class serves as a fundamental data structure for storing
 * time-series financial data. It maintains synchronized vectors for dates
 * and corresponding OHLC price points, providing the foundation for both
 * bid and ask price storage in market data management.
 *
 * Key features:
 * - Thread-safe data storage (read-only after population)
 * - Efficient vector-based storage for time series data
 * - Consistent indexing across all price components
 * - Support for time-based market data operations
 *
 * @note All vectors must maintain the same size for data integrity.
 * @see Market class for usage examples
 */
class BasePrices {
public:
    // ===============================
    // Time Series Data Storage
    // ===============================

    std::vector<TimePoint> dates;  ///< Timestamps for each price data point
    std::vector<double> open;      ///< Opening prices for each time period
    std::vector<double> high;      ///< Highest prices for each time period
    std::vector<double> low;       ///< Lowest prices for each time period
    std::vector<double> close;     ///< Closing prices for each time period

    // ===============================
    // Navigation and State
    // ===============================

    size_t time_idx;  ///< Current time index for iterating through the data

    /**
     * @brief Add a new OHLC data point to all vectors simultaneously
     *
     * This method ensures data consistency by adding corresponding values
     * to all price and date vectors in a single operation. It maintains
     * the synchronized indexing required for proper time series analysis.
     *
     * @param date Timestamp for this data point
     * @param open Opening price for this time period
     * @param low Lowest price reached during this time period
     * @param high Highest price reached during this time period
     * @param close Closing price for this time period
     *
     * @note Parameters are intentionally ordered as (date, open, low, high, close)
     *       which differs from the typical OHLC order for API consistency
     * @post All vectors will have increased size by 1 and maintain synchronization
     */
    void push_back(const TimePoint &date, const double &open, const double &low, const double &high, const double &close) {
        this->dates.push_back(date);
        this->open.push_back(open);
        this->low.push_back(low);
        this->high.push_back(high);
        this->close.push_back(close);
    }
};


/**
 * @class Market
 * @brief Comprehensive market data container and CSV parser for trading simulations
 *
 * The Market class provides complete functionality for loading, storing, and managing
 * financial market data required for realistic trading simulations. It handles both
 * bid and ask price data, supports various CSV formats, and maintains temporal
 * relationships essential for backtesting trading strategies.
 *
 * Key capabilities:
 * - Dual-side market data (bid/ask spreads)
 * - Flexible CSV parsing with column auto-detection
 * - Time-based data filtering and validation
 * - Currency pair and pip value management
 * - Data integrity verification and error handling
 *
 * Typical workflow:
 * 1. Create Market instance
 * 2. Load data from CSV using load_from_csv()
 * 3. Access bid/ask data through respective BasePrices objects
 * 4. Use in trading simulation with proper time indexing
 *
 * @note Market data is assumed to be in chronological order
 * @see BasePrices for underlying data structure details
 */
class Market {

public:
    // ===============================
    // Core Market Data
    // ===============================

    BasePrices ask;  ///< Ask (sell) price data - price at which market participants can buy
    BasePrices bid;  ///< Bid (buy) price data - price at which market participants can sell
    std::vector<TimePoint> dates;  ///< Master timestamp vector (synchronized with bid/ask data)

    // ===============================
    // Market Metadata
    // ===============================

    std::string currencies;        ///< Currency pair identifier (e.g., "EUR/USD", "GBP/JPY")
    TimePoint start_date;         ///< First timestamp in the dataset
    TimePoint end_date;           ///< Last timestamp in the dataset
    size_t number_of_elements;    ///< Total number of data points loaded
    double pip_value;             ///< Value of one pip for this currency pair
    Duration interval;            ///< Time interval between consecutive data points

    // ===============================
    // Constructors
    // ===============================

    /**
     * @brief Default constructor
     *
     * Initializes an empty market with default values. Data must be loaded
     * separately using load_from_csv() or other loading methods.
     */
    Market() {}

    // ===============================
    // Utility Methods
    // ===============================

    /**
     * @brief Calculate the total time span covered by the market data
     *
     * @return Duration representing the time difference between start_date and end_date
     * @note Requires start_date and end_date to be properly initialized
     */
    Duration get_duration() const {return end_date - start_date;}

    /**
     * @brief Display market data summary and sample entries to console
     *
     * Outputs a formatted summary of the loaded market data including:
     * - Currency pair information
     * - Date range and total duration
     * - Number of data points
     * - Sample bid/ask prices
     * - Data quality indicators
     *
     * @note Useful for debugging and data validation
     * @post Prints formatted output to stdout
     */
    void display_market_data() const;

    /**
     * @brief Parse a datetime string into a TimePoint object
     *
     * Converts various datetime string formats commonly found in financial
     * CSV files into standardized TimePoint objects. Supports multiple
     * formats including ISO 8601 and common trading platform formats.
     *
     * @param datetime_string String representation of date and time
     * @return TimePoint object representing the parsed datetime
     * @throws std::invalid_argument if the datetime string format is not recognized
     * @note Timezone handling depends on the input format specification
     */
    TimePoint parse_date_time(const std::string& datetime_string);

    /**
     * @brief Load market data from a CSV file with automatic column detection
     *
     * Parses a CSV file containing OHLC market data with flexible column mapping.
     * Automatically detects column positions based on header names and loads
     * data within the specified time span. Supports both bid-only and bid/ask
     * data formats.
     *
     * Expected CSV format:
     * - Header line with column names
     * - Date/time column (various formats supported)
     * - OHLC columns for bid and/or ask prices
     * - Optional volume or other metadata columns (ignored)
     *
     * @param filename Path to the CSV file to load
     * @param time_span Maximum duration of data to load from file start
     *
     * @throws std::runtime_error if file cannot be opened or parsed
     * @throws std::invalid_argument if required columns are missing
     * @post Market object is populated with parsed data, metadata updated
     * @note File is expected to be sorted chronologically
     */
    void load_from_csv(const std::string& filename, const Duration& time_span);

    // ===============================
    // CSV Parsing Infrastructure
    // ===============================

    /**
     * @struct ColumnIndices
     * @brief Maps CSV column names to their numeric indices for parsing
     *
     * This structure maintains the mapping between expected column names and their
     * positions in the CSV file. It enables flexible CSV parsing where columns
     * can appear in any order as long as they have recognizable headers.
     *
     * The SIZE_MAX value indicates that a particular column was not found in
     * the CSV header, allowing the parser to handle optional columns gracefully.
     *
     * @note All indices are initialized to SIZE_MAX (not found) by default
     * @see parse_header() for automatic column detection
     */
    struct ColumnIndices {
        size_t date       = SIZE_MAX;  ///< Index of date/timestamp column
        size_t ask_open   = SIZE_MAX;  ///< Index of ask opening price column
        size_t ask_high   = SIZE_MAX;  ///< Index of ask high price column
        size_t ask_low    = SIZE_MAX;  ///< Index of ask low price column
        size_t ask_close  = SIZE_MAX;  ///< Index of ask closing price column
        size_t bid_open   = SIZE_MAX;  ///< Index of bid opening price column
        size_t bid_high   = SIZE_MAX;  ///< Index of bid high price column
        size_t bid_low    = SIZE_MAX;  ///< Index of bid low price column
        size_t bid_close  = SIZE_MAX;  ///< Index of bid closing price column
    };

    /**
     * @brief Parse CSV header line to automatically detect column positions
     *
     * Analyzes the header line of a CSV file to determine which columns contain
     * the required market data fields. Uses fuzzy matching to handle variations
     * in column naming conventions across different data providers.
     *
     * Recognized column patterns (case-insensitive):
     * - Date/Time: "date", "time", "datetime", "timestamp"
     * - Ask prices: "ask_open", "ask_high", "ask_low", "ask_close"
     * - Bid prices: "bid_open", "bid_high", "bid_low", "bid_close"
     * - Alternative formats: "open_ask", "high_ask", etc.
     *
     * @param header_line First line of CSV file containing column names
     * @return ColumnIndices struct with populated column positions
     * @throws std::invalid_argument if critical columns (date, prices) are missing
     * @note This is a static method - no Market instance required
     */
    static ColumnIndices parse_header(const std::string& header_line);

    /**
     * @brief Parse a single CSV data line and populate market data vectors
     *
     * Processes one line of CSV data according to the provided column mapping,
     * extracting and validating all available price data. Handles data filtering
     * based on time constraints and provides fallback mechanisms for missing data.
     *
     * Data validation includes:
     * - Timestamp parsing and range checking
     * - Price value validation (positive, reasonable ranges)
     * - Bid-ask spread consistency verification
     * - OHLC logical relationships (low ≤ open,close ≤ high)
     *
     * @param fields Vector of strings representing split CSV line
     * @param cols Column mapping structure from parse_header()
     * @param first_ts Reference timestamp for time span calculations
     * @param time_span Maximum duration to include from first_ts
     * @param fallback_spread Default spread to use if bid data is missing
     * @param spread_override Optional fixed spread override for all data
     * @param first_entry Reference flag indicating if this is the first valid entry
     *
     * @throws std::invalid_argument if required data fields are malformed
     * @post Updates ask, bid, and dates vectors with new data point
     * @note Modifies the first_entry flag when processing initial data point
     */
    void parse_record(const std::vector<std::string>& fields, const ColumnIndices& cols, const TimePoint& first_ts, const Duration& time_span, double fallback_spread, std::optional<double> spread_override, bool& first_entry);

    /**
     * @brief Split a CSV line into individual field strings
     *
     * Performs basic CSV line splitting using comma delimiters. This is a
     * simplified implementation that does not handle quoted fields containing
     * commas or other advanced CSV features.
     *
     * Limitations:
     * - No support for quoted fields with embedded commas
     * - No escape sequence handling
     * - Assumes clean, well-formed CSV data
     *
     * @param line Single line of CSV text to split
     * @return Vector of strings, one per CSV field
     * @note For complex CSV files, consider using a dedicated CSV parsing library
     * @warning Does not handle quoted fields - use only with simple CSV formats
     */
    static std::vector<std::string> split_csv_line(const std::string& line);

    /**
     * @brief Add a new market data point with both ask and bid OHLC prices
     *
     * Programmatically adds a complete market data entry including timestamp,
     * ask prices (open, high, low, close), and bid prices (open, high, low, close).
     * This method is essential for creating market data programmatically for testing,
     * simulation, or when integrating with real-time data feeds.
     *
     * Data validation performed:
     * - Ensures chronological order (timestamp >= last timestamp)
     * - Validates OHLC relationships (low <= open,close <= high)
     * - Verifies bid-ask spread consistency (bid <= ask)
     * - Updates market metadata (start_date, end_date, number_of_elements)
     *
     * @param timestamp Timestamp for this market data point
     * @param ask_open Ask opening price for this time period
     * @param ask_high Ask highest price reached during this time period
     * @param ask_low Ask lowest price reached during this time period
     * @param ask_close Ask closing price for this time period
     * @param bid_open Bid opening price for this time period
     * @param bid_high Bid highest price reached during this time period
     * @param bid_low Bid lowest price reached during this time period
     * @param bid_close Bid closing price for this time period
     *
     * @throws std::invalid_argument if OHLC relationships are violated or bid > ask
     * @throws std::logic_error if timestamp is earlier than the last timestamp
     * @post Updates ask, bid, and dates vectors; updates market metadata
     * @note Automatically maintains data integrity and chronological ordering
     */
    void add_market_data(const TimePoint& timestamp, double ask_open, double ask_high, double ask_low, double ask_close, double bid_open, double bid_high, double bid_low, double bid_close);

    /**
     * @brief Add a new market data point with single ask and bid prices
     *
     * Simplified method for adding market data when only single ask and bid prices
     * are available (typically closing prices). This method automatically sets
     * all OHLC values to the provided ask and bid prices, making it suitable for
     * tick data or simplified market simulations.
     *
     * @param timestamp Timestamp for this market data point
     * @param ask_price Ask price (used for all OHLC values)
     * @param bid_price Bid price (used for all OHLC values)
     *
     * @throws std::invalid_argument if bid_price > ask_price
     * @throws std::logic_error if timestamp is earlier than the last timestamp
     * @post Updates ask, bid, and dates vectors with simplified OHLC data
     * @note This is a convenience method that calls add_market_data() with identical OHLC values
     */
    void add_tick(const TimePoint& timestamp, double ask_price, double bid_price);
};