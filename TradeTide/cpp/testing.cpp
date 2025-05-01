#include "market/market.cpp"
#include "signal/signal.cpp"
#include "position/position.cpp"
#include "risk_managment/risk_managment.cpp"
#include "position_collection/position_collection.cpp"
#include "utils.h"

int main()
{
    Market market = generate_market();

    Signal signal(market);
    signal.generate_random();

    RiskManagment risk_managment(1000, 100, 10, 10);

    std::unique_ptr<BasePosition> position;

    PositionCollection position_collection(
        market,
        signal.trade_signal,
        risk_managment
    );

    position_collection.open_positions();

    position_collection.close_positions();

    position_collection.display();

    return 0;
}