from chatbot.exceptions.ParamException import ParamException
from chatbot.helpers.ParamHelpers.ParamHelper import ParamHelper
from chatbot.helpers.ParamHelpers.ParamTransformer import ParamTransformer
from chatbot.helpers.ParamHelpers.ParamValidator import ParamValidator
from finance.exceptions.MoexExceptions import RequestException


def export(params_dict):
    ticker = params_dict['ticker']
    period = params_dict['period']
    timeframe = params_dict['timeframe']

    validate_params(ticker, period, timeframe)
    timeframe, period = ParamTransformer.transform_timeframe_period(timeframe, period)

    ts = ParamHelper.ts_from_param_period(ticker, timeframe, period)
    if ts.is_empty():
        raise RequestException('ticker')

    return ts.export_xlsx()


def validate_params(ticker, period, timeframe):
    if period is None:
        raise ParamException('no_period')
    elif ticker is None:
        raise ParamException('no_ticker')
    elif not ParamValidator.is_correct_period(period):
        raise ParamException('period')
    elif not ParamValidator.is_correct_timeframe(timeframe):
        raise ParamException('timeframe')