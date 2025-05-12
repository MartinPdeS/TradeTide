#include "../market/market.h"
#include "../signal/signal.h"
#include "../position/position.h"
#include "../risk_managment/risk_managment.h"
#include "../signal/signal.h"


using PositionPtr = std::unique_ptr<BasePosition>;
using TimePoint   = std::chrono::system_clock::time_point;

class PositionCollection{
    public:
        const Market &market;
        PipManager &risk_managment;
        const Signal &signal;
        std::vector<PositionPtr> positions;
        size_t number_of_trade;


        PositionCollection(const Market& market, PipManager &risk_managment, const Signal& signal)
        : market(market), risk_managment(risk_managment), signal(signal)
        {
            this->number_of_trade = std::count_if(signal.trade_signal.begin(), signal.trade_signal.end(), [](int x){ return x != 0; });

            positions.reserve(number_of_trade);
        }

        const PositionPtr& operator[](size_t i) const { return this->positions[i]; }
        void open_positions();
        void close_positions();
        void terminate_open_positions();

        void display();


        template <typename dtype, typename function>
        std::vector<dtype> extract_vector(function accessor){
            std::vector<dtype> array;
            array.reserve(this->positions.size());

            for (const PositionPtr& position : this->positions)
                array.push_back(accessor(position));

            return array;
        }

        std::vector<TimePoint> get_start_dates(){
            return this->extract_vector<TimePoint>([](const PositionPtr& p){return p->start_date;});
        }

        std::vector<TimePoint> get_stop_dates(){
            return this->extract_vector<TimePoint>([](const PositionPtr& p){return p->close_date;});
        }

        std::vector<double> get_entry_prices(){
            return this->extract_vector<double>([](const PositionPtr& p){return p->entry_price;});
        }

        std::vector<double> get_exit_prices(){
            return this->extract_vector<double>([](const PositionPtr& p){return p->exit_price;});
        }

        const Market& get_market() const { return market; }

        /// @brief Return up to `count` Long positions (or all if count==SIZE_MAX).
        std::vector<Long*> get_long_positions(size_t count = SIZE_MAX) const;

        /// @brief Return up to `count` Short positions (or all if count==SIZE_MAX).
        std::vector<Short*> get_short_positions(size_t count = SIZE_MAX) const;

        /// @brief Return up to `count` of all positions (Long and Short).
        std::vector<BasePosition*> get_all_positions(size_t count = SIZE_MAX) const;
};
