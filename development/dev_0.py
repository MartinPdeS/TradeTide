from TradeTide.binary import Portfolio, Position, Market, RiskManagement
from datetime import datetime, timedelta



# Define start and end dates
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 1, 3)

risk_manager = RiskManagement(
    initial_balance=100000,
    risk_per_trade=1.0,
    stop_loss=50,
    take_profit=50
)


market = Market(currencies="EUR/USD")

market.load_from_csv(
    "TradeTide/TradeTide/data/eur_usd/2023/data.csv",
    time_span=timedelta(days=1)
)

# market.generate_random_market_data_minutes(
#     start=start_date,
#     end=end_date,
# )


# market.display_market_data()

# portfolio = Portfolio(risk_manager=risk_manager)

# portfolio.process_signals(

# )

# portfolio.print_metrics(risk_free_rate=2.0)