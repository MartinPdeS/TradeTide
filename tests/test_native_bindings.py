"""Smoke tests that ensure the compiled public bindings are importable."""

from importlib import import_module

import pytest


@pytest.mark.parametrize(
    ("module_name", "symbol"),
    [
        ("TradeTide.market", "Market"),
        ("TradeTide.strategy", "Strategy"),
        ("TradeTide.position", "BasePosition"),
        ("TradeTide.portfolio", "Portfolio"),
        ("TradeTide.backtester", "BACKTESTER"),
        ("TradeTide.indicators", "BOLLINGERBANDS"),
    ],
)
def test_native_binding_exports_its_public_symbol(
    module_name: str, symbol: str
) -> None:
    """Every core native module loads and exposes its documented entry point."""
    module = import_module(module_name)

    assert hasattr(module, symbol)


def test_native_market_round_trip_preserves_a_tick() -> None:
    """A basic native call round-trip catches ABI and conversion regressions."""
    from datetime import datetime

    from TradeTide.market import Market

    market = Market()
    market.add_tick(datetime(2024, 1, 1), ask_price=1.1002, bid_price=1.1000)

    assert len(market.dates) == 1
    assert market.ask.close == pytest.approx([1.1002])
    assert market.bid.close == pytest.approx([1.1000])
