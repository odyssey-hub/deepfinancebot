import pandas as pd

from finance.Indice import Indice


def ticker_indices(params_dict):
    ticker = params_dict['ticker']
    only_branches = params_dict['only_branches']
    indices = Indice.ticker_indices(ticker, only_branches)
    return convert_to_table(indices)


def convert_to_table(indices):
    table = pd.DataFrame()
    table['Индекс'] = indices
    table.index = table.index + 1
    return table