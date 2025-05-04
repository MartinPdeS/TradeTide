#include "backtester.h"


// Run the backtest
void Backtester::run() {
    std::cout << "Running backtest...\n";
    for (const auto& signal : signals) {
        const std::string& currency_pair = std::get<0>(signal);
        bool is_long = std::get<1>(signal);
        double entry_price = std::get<2>(signal);
        double pip_value = std::get<3>(signal);
    }

    // Display results
    std::cout << "\nBacktest complete.\n";
    portfolio.display_positions();
}
