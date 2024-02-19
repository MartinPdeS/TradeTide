from TradeTide import directories
import pandas
import numpy
import pathlib
from MPSPlots.render2D import SceneList
import matplotlib.pyplot as plt


def get_data_path(currency_0: str, currency_1: str, year: int) -> pathlib.Path:
    data_folder = directories.data

    data_file = data_folder / f"{currency_0}_{currency_1}" / str(year) / "data"

    return data_file


def get_dataframe(currency_0: str, currency_1: str, year: int) -> pandas.DataFrame:
    data_file = get_data_path(
        currency_0=currency_0,
        currency_1=currency_1,
        year=year
    )

    dataframe = pandas.read_csv(
        filepath_or_buffer=data_file.with_suffix('.csv'),
    )

    date = pandas.to_datetime(dataframe['date'])

    date = date.dt.tz_localize('Europe/London')

    date = date.dt.tz_convert('UTC')

    dataframe['date'] = date

    dataframe['time_stamp'] = pandas.to_timedelta(dataframe['date'] - dataframe['date'][0])

    dataframe['time_delta'] = dataframe['date'].diff()

    return dataframe


def plot_currencies(currency_0: str, currency_1: str, year: int) -> SceneList:
    dataframe = get_dataframe(
        currency_0=currency_0,
        currency_1=currency_1,
        year=year
    )

    dataframe[['open', 'close']].plot(title='Currencies')

    plt.show()


def convert_xlsx_to_csv(currency_0: str, currency_1: str, year: int) -> None:
    data_file = get_data_path(
        currency_0=currency_0,
        currency_1=currency_1,
        year=year
    )

    dataframe = pandas.read_excel(data_file.with_suffix('.xlsx'))

    columns = [
        'date', 'open', 'high', 'low', 'close', 'volume'
    ]

    dataframe.columns = columns

    dataframe.to_csv(data_file.with_suffix('.csv'), index=False)


def get_crossings(metric_0: object, metric_1: object) -> pandas.DataFrame:
    difference = metric_0.values - metric_1.values

    # output = difference > 0
    output = (numpy.sign(difference.shift(1)) > 0) * (numpy.sign(difference) < 0)
    # output = numpy.sign(difference.shift(1)) != numpy.sign(difference)

    return output

