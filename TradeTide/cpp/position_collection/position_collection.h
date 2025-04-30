#include "../market/market.h"
#include "../signal/signal.h"
#include "../position/position.h"
#include "../risk_managment/risk_managment.h"


using PositionPtr = std::unique_ptr<BasePosition>;


class PositionCollection{
    public:
        const Market &market;
        const std::vector<int>& trade_signal;
        const RiskManagement &risk_managment;
        std::vector<PositionPtr> positions;
        size_t number_of_trade;


        PositionCollection(const Market& market, const std::vector<int> &trade_signal, const RiskManagement &risk_managment)
        : market(market), trade_signal(trade_signal), risk_managment(risk_managment) {
            size_t number_of_trade = std::count_if(trade_signal.begin(), trade_signal.end(), [](int x){ return x != 0; });
            positions.reserve(number_of_trade);
        }

        void open_positions();

        void close_positions();

        void display();
};
