from chatbot.exceptions.ParamException import ParamException
from finance.exceptions.MoexExceptions import RequestException
from chatbot.helpers.ParamHelpers.ParamParser import ParamParser
from chatbot.helpers.ParamHelpers.ParamTransformer import ParamTransformer
from chatbot.helpers.ParamHelpers.ParamValidator import ParamValidator
from finance.FinTimeSeries import FinTimeSeries
from finance.FinTSComparator import FinTSComparator


def corr(params_dict):
    tickers = params_dict['tickers']
    period = params_dict['period']
    timeframe = params_dict['timeframe']
    columns = params_dict['columns']

    validate_params(tickers, period, timeframe, columns)
    timeframe, period = ParamTransformer.transform_timeframe_period(timeframe, period)

    if len(tickers) == 1:
        result = corr_one_ticker(tickers[0], period, timeframe, columns)
    else:
        result = corr_many_tickers(tickers, period, timeframe, columns)

    return result


def corr_one_ticker(ticker, period,  timeframe, columns):
    if columns is None:
        columns = FinTimeSeries.STD_COLUMNS

    if len(columns) < 2:
        raise ParamException('columns')

    if len(period) == 1:
        period = period[0]
        period_type, period_num = ParamParser.extract_period_num_and_type(period)
        ts = FinTimeSeries.from_last(ticker, period_type, period_num, timeframe)
    else:
        start = period[0]
        end = period[1]
        ts = FinTimeSeries(ticker, timeframe, start, end)

    if ts.is_empty():
        raise RequestException('ticker')

    return ts.corr(columns)


def corr_many_tickers(tickers, period, timeframe, columns):
    if columns is None:
        column = 'close'
    else:
        column = columns[0]

    if len(period) == 1:
        period = period[0]
        period_type, period_num = ParamParser.extract_period_num_and_type(period)
        return FinTSComparator.corr(tickers, period_type, period_num, timeframe, column)
    else:
        start = period[0]
        end = period[1]
        return FinTSComparator.corr(tickers, 'p', None, timeframe, column=column, start=start, end=end)


def validate_params(tickers, period, timeframe, columns):
    if period is None:
        raise ParamException('no_period')
    elif tickers is None:
        raise ParamException('no_tickers')
    elif not ParamValidator.is_correct_period(period):
        raise ParamException('period')
    elif not ParamValidator.is_correct_timeframe(timeframe):
        raise ParamException('timeframe')
    elif not ParamValidator.is_correct_columns(columns):
        raise ParamException('columns')






