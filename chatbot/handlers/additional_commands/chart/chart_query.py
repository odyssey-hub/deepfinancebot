from chatbot.exceptions.ParamException import ParamException
from chatbot.helpers.ParamHelpers.ParamHelper import ParamHelper
from chatbot.helpers.ParamHelpers.ParamTransformer import ParamTransformer
from chatbot.helpers.ParamHelpers.ParamValidator import ParamValidator
from finance.Visualizer import Visualizer
from finance.exceptions.MoexExceptions import RequestException


def chart(params_dict):
    tickers = params_dict['tickers']
    period = params_dict['period']
    timeframe = params_dict['timeframe']
    column = params_dict['column']
    is_candles_chart = params_dict['is_candles_chart']
    is_image = params_dict['is_image']

    validate_params(tickers, period, timeframe, column)
    timeframe, period = ParamTransformer.transform_timeframe_period(timeframe, period)
    if is_image:
        file_format = 'png'
    else:
        file_format = 'html'

    if len(tickers) == 1:
        path = chart_one_ticker(tickers[0], period, timeframe, column, is_candles_chart, file_format)
    else:
        path = chart_many_tickers(tickers, period, timeframe, column, file_format)

    return path


def chart_one_ticker(ticker, period, timeframe, column, is_candle_chart, file_format):
    ts = ParamHelper.ts_from_param_period(ticker, timeframe, period)
    if ts.is_empty():
        raise RequestException('ticker')
    if is_candle_chart:
        return Visualizer.candle_chart(ts, format=file_format)
    else:
        return Visualizer.line_chart([ts], column, format=file_format)


def chart_many_tickers(tickers, period, timeframe, column, file_format):
    list_ts = list()
    for ticker in tickers:
        ts = ParamHelper.ts_from_param_period(ticker, timeframe, period)
        if ts.is_empty():
            raise RequestException('ticker')
        list_ts.append(ts)
    return Visualizer.line_chart(list_ts, column, format=file_format)


def validate_params(tickers, period, timeframe, column):
    if period is None:
        raise ParamException('no_period')
    elif tickers is None:
        raise ParamException('no_tickers')
    elif not ParamValidator.is_correct_period(period):
        raise ParamException('period')
    elif not ParamValidator.is_correct_timeframe(timeframe):
        raise ParamException('timeframe')
    elif not ParamValidator.is_correct_column(column):
        raise ParamException('columns')