// Position.h
#pragma once

// Define the Position C++ class
class Position
{
    public:
        Position(double entry, double exit) : entry_price(entry), exit_price(exit) {}
        double profit() const { return exit_price - entry_price; }
        double lol = 1.0;
    private:
        double entry_price;
        double exit_price;
};