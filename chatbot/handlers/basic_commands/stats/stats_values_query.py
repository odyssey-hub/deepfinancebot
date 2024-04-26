from chatbot.exceptions.ParamException import ParamException
from chatbot.helpers.ParamHelpers.ParamHelper import ParamHelper
from chatbot.helpers.ParamHelpers.ParamTransformer import ParamTransformer
from chatbot.helpers.ParamHelpers.ParamValidator import ParamValidator
from finance.exceptions.MoexExceptions import RequestException


def stats_values(stats_value, params_dict):
    ticker = params_dict['ticker']
    period = params_dict['period']
    timeframe = params_dict['timeframe']
    column = params_dict['column']

    validate_params(ticker, period, timeframe, column)
    timeframe, period = ParamTransformer.transform_timeframe_period(timeframe, period)

    ts = ParamHelper.ts_from_param_period(ticker, timeframe, period)
    if ts.is_empty():
        raise RequestException('ticker')

    stats_func = ts.mean

    if stats_value == 'mean':
        stats_func = ts.mean
    elif stats_value == 'var':
        stats_func = ts.var
    elif stats_value == 'median':
        stats_func = ts.median
    elif stats_value == 'std':
        stats_func = ts.std

    if column == 'all':
        precision = 4
        result = f"Close  {round(stats_func('close'), precision)}\n"
        result += f"Open  {round(stats_func('open'), precision)}\n"
        result += f"High  {round(stats_func('high'), precision)}\n"
        result += f"Low  {round(stats_func('low'), precision)}\n"
        result += f"Volume {stats_func('volume')}\n"
        return result

    return stats_func(column)


def validate_params(ticker, period, timeframe, column):
    if period is None:
        raise ParamException('no_period')
    elif ticker is None:
        raise ParamException('no_ticker')
    elif not ParamValidator.is_correct_period(period):
        raise ParamException('period')
    elif not ParamValidator.is_correct_timeframe(timeframe):
        raise ParamException('timeframe')
    elif not ParamValidator.is_correct_column(column):
        if column == 'all':
            return
        raise ParamException('columns')



