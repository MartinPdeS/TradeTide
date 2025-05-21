#include "signal.h"


void Signal::generate_random(double probability) {
    std::mt19937 rng(std::random_device{}());
    std::uniform_real_distribution<double> dist(0.0, 1.0);
    std::bernoulli_distribution direction(0.5);

    this->trade_signal.clear();
    for (size_t i = 0; i < this->market.dates.size(); ++i) {
        if (dist(rng) < probability) {
            this->trade_signal.push_back(direction(rng) ? 1 : -1);
        } else {
            this->trade_signal.push_back(0);
        }
    }
}

const std::vector<int>& Signal::get_signals() const {
    return this->trade_signal;
}

void Signal::display(size_t max_count) const {
    std::cout << "Trade Signals [timestamp, signal]:\n";
    for (size_t i = 0; i < std::min(max_count, this->trade_signal.size()); ++i) {
        std::time_t t = std::chrono::system_clock::to_time_t(this->market.dates[i]);
        std::cout << std::put_time(std::localtime(&t), "%Y-%m-%d %H:%M:%S")
                    << " => " << this->trade_signal[i] << "\n";
    }
    if (this->trade_signal.size() > max_count) {
        std::cout << "... (" << this->trade_signal.size() << " total signals)\n";
    }
}

void Signal::to_csv(const std::string& filepath) const {
    std::ofstream file(filepath);
    if (!file.is_open())
        throw std::runtime_error("Unable to open file: " + filepath);

    // Write metadata
    file << "#METADATA:\n";
    file << "#is_bid=" << (this->market.is_bid ? "true" : "false") << "\n";
    file << "#pip_size=" << this->market.pip_value << "\n";

    // Write header
    file << "#DATA\n";
    file << "timestamp,signal\n";

    // Write data
    for (size_t i = 0; i < this->trade_signal.size(); ++i) {
        std::time_t t = std::chrono::system_clock::to_time_t(this->market.dates[i]);
        file << std::put_time(std::localtime(&t), "%Y-%m-%d %H:%M:%S") << ","
             << this->trade_signal[i] << "\n";
    }

    file.close();
}



std::pair<size_t, size_t> Signal::count_signals() const {
    size_t long_count = 0, short_count = 0;
    for (int s : this->trade_signal) {
        if (s == 1) ++long_count;
        else if (s == -1) ++short_count;
    }
    return { long_count, short_count };
}


bool Signal::validate_against_market() const {
    return this->trade_signal.size() == this->market.dates.size();
}


std::vector<int> Signal::compute_trade_signal() {
    // Could be implemented based on price movement or technical rules.
    return this->trade_signal;
}
