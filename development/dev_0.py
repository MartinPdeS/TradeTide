from TradeTide.binary import Portfolio, Position, Market, RiskManagement
from datetime import datetime

# Define start and end dates
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)

risk_manager = RiskManagement(
    initial_balance=100000,
    risk_per_trade=1.0,
    stop_loss=50,
    take_profit=50
)


market = Market(
    start_date=start_date,
    end_date=end_date
)


market.display_market_data()

# portfolio = Portfolio(risk_manager=risk_manager)

# portfolio.process_signals(

# )

# portfolio.print_metrics(risk_free_rate=2.0)