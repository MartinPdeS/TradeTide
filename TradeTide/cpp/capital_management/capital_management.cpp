#include "capital_management.h"

#include "../position/position.h"

// Update account balance
// void
// Riskmanagement::update_balance(double new_balance) {
//     account_balance = new_balance;
// }

// // Calculate position size
// double
// Riskmanagement::calculate_position_size(const double entry_price, const double pip_value) const {
//     // Maximum risk in dollars
//     double max_risk_dollars = (max_risk_per_trade / 100.0) * account_balance;

//     // Lot size based on maximum risk and stop-loss distance
//     double lot_size = max_risk_dollars / (this->stop_loss * pip_value);

//     return lot_size;
// }


// void
// Riskmanagement::update_position_lot_size(BasePosition &position, const double currency_per_pip) const {
//     // Maximum risk in dollars
//     double max_risk_dollars = (this->max_risk_per_trade / 100.0) * this->account_balance;

//     // Lot size based on maximum risk and stop-loss distance
//     double lot_size = max_risk_dollars / (this->stop_loss * currency_per_pip);

//     position.lot_size = lot_size;
// }


// // Enforce risk parameters for a new position
// bool
// Riskmanagement::validate_position(const double entry_price, const double lot_size, const double current_price, const bool is_long) const {
//     // Calculate stop-loss and maximum risk
//     double stop_loss_price = entry_price - (is_long ? this->stop_loss : -this->stop_loss);
//     double potential_loss = abs(entry_price - stop_loss_price) * lot_size;

//     return potential_loss <= (max_risk_per_trade / 100.0) * account_balance;
// }