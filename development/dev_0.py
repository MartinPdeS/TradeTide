from TradeTide.binary import PortfolioInterface


risk_manager = PortfolioInterface.RiskManagement(
    initial_balance=100000, 
    risk_per_trade=1.0, 
    stop_loss=50
)

portfolio = PortfolioInterface.Portfolio(risk_manager=risk_manager)

portfolio.add_position(
    currency_pair="EUR/USD", 
    is_long=True, 
    entry_price=1.1000, 
    pip_value=10.0
)

portfolio.print_metrics(risk_free_rate=2.0)