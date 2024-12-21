#include <iostream>
#include "portfolio.cpp"
#include "signal.cpp"
#include "risk_managment.cpp"
// #include "backtester.cpp"


int main() {
    // Initialize Market and Signal
    std::time_t start_date = std::time(nullptr);
    std::time_t end_date = start_date + 10 * 24 * 60 * 60; // 10 days of data
    Market market(start_date, end_date);
    Signal signal(market);

    signal.generate_random();

    // Initialize Risk Management and Portfolio
    RiskManagement risk_manager(100000, 1.0, 50);
    Portfolio portfolio(risk_manager);

    // Process signals with pip price, stop-loss, and take-profit
    portfolio.process_signals(signal, market, 10.0, 0.002, 0.004); // Pip price = $10, SL = 0.002, TP = 0.004

    // Display portfolio and metrics
    portfolio.display_positions();
    return 0;
}

