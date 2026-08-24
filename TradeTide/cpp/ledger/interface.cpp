#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <numeric>
#include <string>
#include <vector>

namespace py = pybind11;

struct LedgerEntry {
    std::size_t trade_id;
    py::object entry_time;
    py::object exit_time;
    std::string side;
    double entry_price;
    double exit_price;
    double lot_size;
    double gross_pnl;
    double net_pnl;
    double total_cost;
    std::string exit_reason;
    py::object holding_period;
    double maximum_adverse_excursion;
    double maximum_favorable_excursion;
};

struct PositionAnalytics {
    std::size_t long_trades;
    std::size_t short_trades;
    py::object average_holding_period;
    double expectancy;
    double average_win;
    double average_loss;
    std::size_t longest_winning_streak;
    std::size_t longest_losing_streak;
    double average_mae;
    double average_mfe;
    double best_trade;
    double worst_trade;
};

std::size_t longest_streak(const std::vector<LedgerEntry>& entries, bool positive) {
    std::size_t longest = 0;
    std::size_t current = 0;
    for (const auto& entry : entries) {
        const bool matches = positive ? entry.net_pnl > 0.0 : entry.net_pnl < 0.0;
        current = matches ? current + 1 : 0;
        longest = std::max(longest, current);
    }
    return longest;
}

PositionAnalytics analyse(const std::vector<LedgerEntry>& entries) {
    double pnl_sum = 0.0, winner_sum = 0.0, loser_sum = 0.0;
    double mae_sum = 0.0, mfe_sum = 0.0, duration_seconds = 0.0;
    std::size_t longs = 0, shorts = 0, winners = 0, losers = 0;
    double best = 0.0, worst = 0.0;
    if (!entries.empty()) {
        best = worst = entries.front().net_pnl;
    }
    for (const auto& entry : entries) {
        pnl_sum += entry.net_pnl;
        mae_sum += entry.maximum_adverse_excursion;
        mfe_sum += entry.maximum_favorable_excursion;
        duration_seconds += py::cast<double>(entry.holding_period.attr("total_seconds")());
        if (entry.side == "long") ++longs; else if (entry.side == "short") ++shorts;
        if (entry.net_pnl > 0.0) { winner_sum += entry.net_pnl; ++winners; }
        if (entry.net_pnl < 0.0) { loser_sum += entry.net_pnl; ++losers; }
        best = std::max(best, entry.net_pnl);
        worst = std::min(worst, entry.net_pnl);
    }
    py::object timedelta = py::module_::import("datetime").attr("timedelta");
    const double count = static_cast<double>(entries.size());
    return {
        longs, shorts, timedelta(py::arg("seconds") = entries.empty() ? 0.0 : duration_seconds / count),
        entries.empty() ? 0.0 : pnl_sum / count,
        winners ? winner_sum / static_cast<double>(winners) : 0.0,
        losers ? loser_sum / static_cast<double>(losers) : 0.0,
        longest_streak(entries, true), longest_streak(entries, false),
        entries.empty() ? 0.0 : mae_sum / count, entries.empty() ? 0.0 : mfe_sum / count,
        best, worst
    };
}

struct TradeLedger {
    std::vector<LedgerEntry> entries;
    PositionAnalytics analytics;

    explicit TradeLedger(std::vector<LedgerEntry> values = {})
        : entries(std::move(values)), analytics(analyse(entries)) {}

    static TradeLedger from_trades(const py::iterable& trades) {
        std::vector<LedgerEntry> entries;
        std::size_t trade_id = 1;
        for (py::handle handle : trades) {
            py::object trade = py::reinterpret_borrow<py::object>(handle);
            py::object entry_time = trade.attr("entry_time");
            py::object exit_time = trade.attr("exit_time");
            py::object costs = trade.attr("costs");
            entries.push_back({
                trade_id++, entry_time, exit_time,
                py::cast<bool>(trade.attr("is_long")) ? "long" : "short",
                py::cast<double>(trade.attr("entry_price")), py::cast<double>(trade.attr("exit_price")),
                py::cast<double>(trade.attr("lot_size")), py::cast<double>(trade.attr("gross_pnl")),
                py::cast<double>(trade.attr("net_pnl")), py::cast<double>(costs.attr("total")),
                py::cast<std::string>(trade.attr("exit_reason")), exit_time.attr("__sub__")(entry_time),
                py::cast<double>(trade.attr("maximum_adverse_excursion")),
                py::cast<double>(trade.attr("maximum_favorable_excursion"))
            });
        }
        return TradeLedger(std::move(entries));
    }

    py::list to_dicts() const {
        py::list rows;
        for (const auto& entry : entries) {
            py::dict row;
            row["trade_id"] = entry.trade_id;
            row["entry_time"] = entry.entry_time;
            row["exit_time"] = entry.exit_time;
            row["side"] = entry.side;
            row["entry_price"] = entry.entry_price;
            row["exit_price"] = entry.exit_price;
            row["lot_size"] = entry.lot_size;
            row["gross_pnl"] = entry.gross_pnl;
            row["net_pnl"] = entry.net_pnl;
            row["total_cost"] = entry.total_cost;
            row["exit_reason"] = entry.exit_reason;
            row["holding_period"] = entry.holding_period;
            row["maximum_adverse_excursion"] = entry.maximum_adverse_excursion;
            row["maximum_favorable_excursion"] = entry.maximum_favorable_excursion;
            rows.append(std::move(row));
        }
        return rows;
    }

    py::object to_dataframe() const {
        return py::module_::import("pandas").attr("DataFrame")(to_dicts());
    }
};

PYBIND11_MODULE(ledger, module) {
    py::class_<LedgerEntry>(module, "LedgerEntry")
        .def(py::init<std::size_t, py::object, py::object, std::string, double, double, double, double, double, double, std::string, py::object, double, double>(),
            py::arg("trade_id"), py::arg("entry_time"), py::arg("exit_time"), py::arg("side"),
            py::arg("entry_price"), py::arg("exit_price"), py::arg("lot_size"), py::arg("gross_pnl"),
            py::arg("net_pnl"), py::arg("total_cost"), py::arg("exit_reason"), py::arg("holding_period"),
            py::arg("maximum_adverse_excursion"), py::arg("maximum_favorable_excursion"))
        .def_readonly("trade_id", &LedgerEntry::trade_id).def_readonly("entry_time", &LedgerEntry::entry_time)
        .def_readonly("exit_time", &LedgerEntry::exit_time).def_readonly("side", &LedgerEntry::side)
        .def_readonly("entry_price", &LedgerEntry::entry_price).def_readonly("exit_price", &LedgerEntry::exit_price)
        .def_readonly("lot_size", &LedgerEntry::lot_size).def_readonly("gross_pnl", &LedgerEntry::gross_pnl)
        .def_readonly("net_pnl", &LedgerEntry::net_pnl).def_readonly("total_cost", &LedgerEntry::total_cost)
        .def_readonly("exit_reason", &LedgerEntry::exit_reason).def_readonly("holding_period", &LedgerEntry::holding_period)
        .def_readonly("maximum_adverse_excursion", &LedgerEntry::maximum_adverse_excursion)
        .def_readonly("maximum_favorable_excursion", &LedgerEntry::maximum_favorable_excursion);

    py::class_<PositionAnalytics>(module, "PositionAnalytics")
        .def_readonly("long_trades", &PositionAnalytics::long_trades).def_readonly("short_trades", &PositionAnalytics::short_trades)
        .def_readonly("average_holding_period", &PositionAnalytics::average_holding_period)
        .def_readonly("expectancy", &PositionAnalytics::expectancy).def_readonly("average_win", &PositionAnalytics::average_win)
        .def_readonly("average_loss", &PositionAnalytics::average_loss)
        .def_readonly("longest_winning_streak", &PositionAnalytics::longest_winning_streak)
        .def_readonly("longest_losing_streak", &PositionAnalytics::longest_losing_streak)
        .def_readonly("average_mae", &PositionAnalytics::average_mae).def_readonly("average_mfe", &PositionAnalytics::average_mfe)
        .def_readonly("best_trade", &PositionAnalytics::best_trade).def_readonly("worst_trade", &PositionAnalytics::worst_trade);

    py::class_<TradeLedger>(module, "TradeLedger")
        .def(py::init<std::vector<LedgerEntry>>(), py::arg("entries") = std::vector<LedgerEntry>{})
        .def_readonly("entries", &TradeLedger::entries).def_readonly("analytics", &TradeLedger::analytics)
        .def_static("from_trades", &TradeLedger::from_trades, py::arg("trades"))
        .def("to_dicts", &TradeLedger::to_dicts).def("to_dataframe", &TradeLedger::to_dataframe);
}
