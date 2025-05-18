#include "../market/market.h"
#include "../signal/signal.h"
#include "../position/position.h"
#include "../exit_strategy/exit_strategy.h"
#include "../signal/signal.h"


using PositionPtr = std::unique_ptr<BasePosition>;
using TimePoint   = std::chrono::system_clock::time_point;

class PositionCollection{
    private:

        template <typename dtype, typename function>
        std::vector<dtype> extract_vector(function accessor){
            std::vector<dtype> array;
            array.reserve(this->positions.size());

            for (const PositionPtr& position : this->positions)
            array.push_back(accessor(position));

            return array;
        }

    public:
        const Market &market;
        ExitStrategy &exit_strategy;
        const Signal &signal;
        std::vector<PositionPtr> positions;
        size_t number_of_trade;

        bool save_price_data = false; // Save the limit price for the position


        PositionCollection(const Market& market, ExitStrategy &exit_strategy, const Signal& signal, const bool save_price_data = false)
        : market(market), exit_strategy(exit_strategy), signal(signal), save_price_data(save_price_data)
        {
            this->number_of_trade = std::count_if(signal.trade_signal.begin(), signal.trade_signal.end(), [](int x){ return x != 0; });

            positions.reserve(number_of_trade);
        }

        void open_positions();
        void close_positions();
        void terminate_open_positions();

        void display();

        BasePosition* __getitem__(const size_t idx) {
            if (idx >= this->positions.size())
                throw std::out_of_range("Index out of range");
            return this->positions[idx].get();                   // return pointer
        }

        size_t __len__() const { return this->positions.size(); }

        [[nodiscard]] size_t size() const { return this->positions.size(); }

        const PositionPtr& operator[](size_t i) const { return this->positions[i]; }


        [[nodiscard]] std::vector<TimePoint> get_start_dates(){
            return this->extract_vector<TimePoint>([](const PositionPtr& p){return p->start_date;});
        }

        [[nodiscard]] std::vector<TimePoint> get_close_dates(){
            return this->extract_vector<TimePoint>([](const PositionPtr& p){return p->close_date;});
        }

        [[nodiscard]] std::vector<double> get_entry_prices(){
            return this->extract_vector<double>([](const PositionPtr& p){return p->entry_price;});
        }

        [[nodiscard]] std::vector<double> get_exit_prices(){
            return this->extract_vector<double>([](const PositionPtr& p){return p->exit_price;});
        }

        const Market& get_market() const { return market; }

        /// @brief Return up to `count` Long positions (or all if count==SIZE_MAX).
        [[nodiscard]] std::vector<Long*> get_long_positions(size_t count) const;

        /// @brief Return up to `count` Short positions (or all if count==SIZE_MAX).
        [[nodiscard]] std::vector<Short*> get_short_positions(size_t count) const;

        /// @brief Return up to `count` of all positions (Long and Short).
        [[nodiscard]] std::vector<BasePosition*> get_all_positions(size_t count) const;
};
