import pandas as pd
from finance.Indice import Indice
from finance.exceptions.MoexExceptions import RequestException


def indice_compound(params_dict):
    indice = Indice(params_dict['indice_name'])

    indice_tickers = indice.tickers_weights()

    if indice_tickers:
        indice_tickers_sorted = {k: v for k, v in sorted(indice_tickers.items(), key=lambda item: item[1], reverse=True)}
        return convert_to_table(indice_tickers_sorted)
    else:
        raise RequestException('indice')


def convert_to_table(indice_tickers: dict):
    table = pd.DataFrame()
    table['Индекс'] = indice_tickers.keys()
    table['Вес'] = indice_tickers.values()
    table.index = table.index + 1
    return table
