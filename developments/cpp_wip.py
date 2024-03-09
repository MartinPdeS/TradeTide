from TradeTide.binaries.interface import Position

pos = Position(entry_price=10, exit_price=150)
print("Profit:", pos.profit())