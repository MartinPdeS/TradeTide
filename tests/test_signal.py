import pytest
import tempfile
from datetime import timedelta

from TradeTide.market import Market
from TradeTide.signal import Signal
from TradeTide.currencies import Currency
from TradeTide.times import days
import TradeTide
TradeTide.debug_mode = True  # Enable debug mode for development purpose

@pytest.fixture
def market():
    market = Market()
    market.load_from_database(
        currency_0=Currency.EUR,
        currency_1=Currency.USD,
        time_span=1 * days,
    )
    return market

def test_signal_length_matches_market(market):
    signal = Signal(market)
    assert len(signal.trade_signal) == len(market.dates), "Signal length does not match market"

def test_generate_random_signal_distribution(market):
    signal = Signal(market)
    signal.generate_random(probability=0.2)
    longs, shorts = signal.count_signals()

    total = longs + shorts
    expected_min = int(0.1 * len(market.dates))  # Loose bounds
    expected_max = int(0.3 * len(market.dates))

    assert expected_min <= total <= expected_max, "Random signal generation is outside expected range"

def test_signal_to_csv(market):
    signal = Signal(market)
    signal.generate_random(probability=0.1)

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=True) as tmp:
        signal.to_csv(tmp.name)
        tmp.seek(0)
        content = tmp.read().decode()
        assert "METADATA" in content, "CSV content seems malformed"

def test_signal_validation(market):
    signal = Signal(market)
    assert signal.validate_against_market(), "Signal failed validation after creation"

if __name__ == "__main__":
    pytest.main(["-W error", __file__])