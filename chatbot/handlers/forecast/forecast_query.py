from chatbot.exceptions.ForecastException import ForecastException
from chatbot.exceptions.ParamException import ParamException
from finance.forecasting.RegForecaster import RegForecaster
from finance.forecasting.StatsForecaster import StatsForecaster
from finance.forecasting.NNForecaster import NNForecaster

from chatbot.helpers.ParamHelpers.ParamValidator import ParamValidator
from chatbot.helpers.ParamHelpers.ParamTransformer import ParamTransformer

from datetime import datetime

def forecast(params_dict):
    ticker = params_dict['ticker']
    timeframe = params_dict['timeframe']
    column = params_dict['column']
    horizon = params_dict['horizon']
    model = params_dict['model']

    period = params_dict['period']
    curr_date = params_dict['date']
    eval_horizon = params_dict['eval_horizon']
    is_prob = params_dict['is_prob']


    period, horizon, eval_horizon = set_default_values(period, horizon, eval_horizon, timeframe, model)

    validate_params(ticker, period, timeframe, column, horizon, eval_horizon, model)
    timeframe, period = ParamTransformer.transform_timeframe_period(timeframe, period)

    forecast_type = detect_forecast_type(model)

    forecast_params = make_forecast_params_dict(ticker, timeframe, column, horizon, model,
                                                is_prob, eval_horizon, period, curr_date)

    return make_forecast(forecast_type, forecast_params)


def make_forecast(forecast_type, forecast_params):
    match forecast_type:
        case 'stat':
            forecaster = StatsForecaster(**forecast_params)
        case 'reg':
            forecaster = RegForecaster(**forecast_params)
        case 'nn':
            forecaster = NNForecaster(**forecast_params)
        case _:
            if forecast_params['is_prob']:
                forecast_params['model_name'] = 'rnn'
            else:
                forecast_params['model_name'] = 'nhits'
            if forecast_params['timeframe'] == 60:
                forecast_params['model_name'] = 'rnn'
            forecaster = NNForecaster(**forecast_params)
    try:
        last_price = forecaster.ts.last_price()
        metrics_dict = forecaster.eval()
        results_df = forecaster.fit_predict()
    except Exception:
        raise ForecastException("learning")

    return metrics_dict, results_df, last_price


def detect_forecast_type(model):
    match model:
        case 'auto':
            forecast_type = 'auto'
        case 'arima' | 'ets':
            forecast_type = 'stat'
        case 'xgboost':
            forecast_type = 'reg'
        case 'rnn' | 'nhits' | 'tcn':
            forecast_type = 'nn'
        case _:
            forecast_type = 0
    return forecast_type

def set_default_values(period, horizon, eval_horizon, timeframe, model):
    if period == '0':
        if timeframe == 'd':
            period = '4y'
        elif timeframe == 'h':
            period = '3m'
        elif timeframe == 'w':
            period = '6y'
    if horizon == 0:
        if timeframe == 'd':
            if model == 'arima' or model == 'ets':
                horizon = 1
            else:
                horizon = 1
        elif timeframe == 'h':
            horizon = 30
        elif timeframe == 'w':
            horizon = 1
    if eval_horizon == 0:
        if timeframe == 'd':
            if model == 'arima' or model == 'ets':
                eval_horizon = 1
            else:
                eval_horizon = 1
        elif timeframe == 'h':
            eval_horizon = 30
        elif timeframe == 'w':
            eval_horizon = 1
    return [period], horizon, eval_horizon

def make_forecast_params_dict(ticker, timeframe, column, horizon, model, is_prob, eval_horizon, period, curr_date):
    forecast_params = {
        "ticker": ticker,
        "timeframe": timeframe,
        "target": column,
        "horizon": horizon,
        "model_name": model,
        "is_prob": is_prob,
        "eval_horizon": eval_horizon,
        "period": period,
    }
    if curr_date:
        curr_date = datetime.strptime(curr_date, "%d.%m.%Y")
        forecast_params['curr_date'] = curr_date
    return forecast_params

def validate_params(ticker, period, timeframe, column, horizon, eval_horizon, model):
    if period is None:
        raise ParamException("no_period")
    elif ticker is None:
        raise ParamException("no_ticker")
    elif not ParamValidator.is_correct_period(period):
        raise ParamException("period")
    elif not ParamValidator.is_correct_timeframe(timeframe):
        raise ParamException("timeframe")
    elif timeframe not in ['d', 'w', 'h']:
        raise ParamException("timeframe")
    elif not ParamValidator.is_correct_column(column):
        raise ParamException("columns")
    elif horizon < 0 or horizon >= 100:
        raise ForecastException("horizon")
    elif eval_horizon < 0 or eval_horizon >= 100:
        raise ForecastException("horizon")
    elif model not in ['auto','arima', 'ets', 'rnn', 'nhits']:
        raise ForecastException("model")



