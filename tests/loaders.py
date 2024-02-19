from TradeTide.tools import get_dataframe


def test_load_dataframe() -> None:
    data_frame = get_dataframe('eur', 'usd', year=2020)


# -
