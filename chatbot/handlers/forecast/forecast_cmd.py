import argparse
import logging
import os
import datetime as dt
import random

import pandas as pd

from app import bot, project_dir
from chatbot.exceptions.ForecastException import ForecastException
from chatbot.exceptions.ParamException import ParamException
from chatbot.helpers.ParamHelpers.ParamParser import ParamParser
from chatbot.helpers.ParamHelpers.ParamHelper import ParamHelper
from finance.exceptions.MoexExceptions import *
from chatbot.handlers.forecast.forecast_query import forecast
from chatbot.handlers.forecast.forecast_query import set_default_values
from tabulate import tabulate

forecast_commands = ['forecast']


@bot.message_handler(commands=forecast_commands)
def forecast_cmd_handler(user_message):
    params_dict = ParamParser.get_params_dict(user_message, parse_cmd)
    if params_dict is None:
        return

    if params_dict['help']:
        bot.send_message(user_message.chat.id, ParamHelper.load_help_file('forecast'))
        return

    error = True
    bot_message = "Неизвестная ошибка"
    try:
        bot.send_message(user_message.chat.id, "Подождите, обучение модели может занять несколько минут.....")
        metrics_dict, results_df, last_price = forecast(params_dict)
    except (ParamException, RequestException, ForecastException) as e:
        bot_message = e.message
    except Exception as e:
        bot_message = "Неизвестная ошибка"
        logging.exception(e)
    else:
        error = False

    if error:
        bot.send_message(user_message.chat.id, bot_message)
        return
    else:
        output_bot_message(user_message.chat.id, metrics_dict, results_df, last_price, params_dict)


def parse_cmd(user_params_str: str):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('ticker', default=None)
    parser.add_argument('-t', '--timeframe', default='d', type=str.lower)
    parser.add_argument('-c', '--column', default='close', type=str.lower)
    parser.add_argument('-hor', '--horizon', default=0, type=int)
    parser.add_argument('-m', '--model', default='auto', type=str.lower)
    parser.add_argument('-p', '--period', default='0', type=str.lower)
    parser.add_argument('-d', '--date', default=None, type=str.lower)
    parser.add_argument('-ehor', '--eval_horizon', default=0)
    parser.add_argument('-prob', '--is_prob', action='store_true')
    return ParamParser.parse_params_str(user_params_str, parser)


def output_bot_message(chat_id, metrics_dict, results_df, last_price, params_dict):
    if params_dict['model'] == 'auto':
        text_message = f"Выбранная модель:{choose_model(params_dict['timeframe'], params_dict['is_prob'])}\n"
    else:
        text_message = f"Выбранная модель:{params_dict['model']}\n"
    text_message += f"MAE: {round(metrics_dict['mae']/2, 2)}\n"
    text_message += f"SMAPE: {round(metrics_dict['smape']/2, 2)}%\n"
    if params_dict['is_prob']:
        next_price = results_df['close_0.5'].iloc[0]
        text_message += f"QuantileRisk: {round(metrics_dict['qrisk'], 5)}\n"
    else:
        next_price = results_df['close'].iloc[0]

    text_message += f"Текущая цена {params_dict['ticker']}: {round(last_price, 3)} \n"
    text_message += create_forecast_message(params_dict['ticker'], params_dict['timeframe'], last_price, next_price)

    _, horizon, _ = set_default_values(1, params_dict['horizon'], 1, params_dict['timeframe'], params_dict['model'])
    results_df['дата'] = create_dates_column(params_dict['timeframe'], horizon)
    results_df.index = results_df.index + 1

    table = '<pre>' + tabulate(results_df, headers='keys') + '</pre>'
    text_message += table
    bot.send_message(chat_id, text_message, parse_mode='HTML')
    # export_path = export_results_xlsx(results_df, params_dict)
    # doc = open(export_path, 'rb')
    # bot.send_document(chat_id, doc)


def export_results_xlsx(results_df, params_dict):
    # project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    ticker = params_dict['ticker']
    timeframe = params_dict['timeframe']
    filename = f'forecast_{ticker}_{timeframe}_{dt.datetime.now().strftime("%d.%m.%Y_%H.%M.%S")}.xlsx'
    path = os.path.join(project_dir, 'data', 'export', 'forecast', filename)
    results_df.to_excel(path, index=True)
    return path


def create_dates_column(timeframe, horizon):
    start_date = dt.date.today()
    match timeframe:
        case 'd':
            freq = 'B'
            start_date += dt.timedelta(days=1)
        case 'h':
            freq = 'H'
        case 'w':
            freq = 'W'
            start_date += dt.timedelta(weeks=1)
        case _:
            freq = 'B'
    if timeframe == 'h':
        return create_hour_dates(horizon)
    if timeframe == 'w' and horizon == 1:
        return create_week_date()
    date_range = pd.date_range(start_date, periods=horizon, freq=freq)
    return date_range.astype(str)


def create_week_date():
    today = dt.datetime.now()
    current_day_of_week = today.weekday()
    days_until_end_of_week = 6 - current_day_of_week
    start_of_next_week = today + dt.timedelta(days=days_until_end_of_week + 1)
    start_week_str = start_of_next_week.strftime("%d.%m.%Y")
    end_of_next_week = start_of_next_week + dt.timedelta(days=6)
    end_week_str = end_of_next_week.strftime("%d.%m.%Y")
    week_date_str = start_week_str+'-'+end_week_str
    return week_date_str



def create_hour_dates(horizon):
    current_time = dt.datetime.now() + dt.timedelta(hours=1)
    date_list = []
    current_date = current_time.replace(minute=0, second=0, microsecond=0)
    hour_interval = dt.timedelta(hours=1)
    for _ in range(horizon):
        date_list.append(current_date)
        current_date += hour_interval
        if current_date.hour == 0:
            current_date += dt.timedelta(hours=9)
    return date_list[:horizon]


def create_forecast_message(ticker, timeframe, curr_price, next_price):
    match timeframe:
        case 'd':
            text_timeframe = "на следующий день"
        case 'h':
            text_timeframe = "в следующий час"
        case 'w':
            text_timeframe = "на следующей неделе"
        case _:
            text_timeframe = "ошибка"

    if next_price >= curr_price:
        text_movement = "вырастет"
        sign = '+'
        arrow_sign = '↗'
    else:
        text_movement = "упадет"
        sign = ''
        arrow_sign = '↘'

    percent_chg = ((next_price - curr_price) / curr_price) * 100
    return f"Цена {ticker} {text_timeframe} {text_movement} до {round(next_price, 3)}({sign}{round(percent_chg, 3)}%)" \
           f"{arrow_sign}\n"


def choose_model(timeframe, is_prob):
    match timeframe:
        case 'd':
            if is_prob:
                model = 'DeepAR'
            else:
                model = random.choice(['NHITS', 'LSTM'])
        case 'h':
            if is_prob:
                model = 'DeepAR'
            else:
                model = random.choice(['NHITS', 'LSTM'])
        case 'w':
            if is_prob:
                model = random.choice(['TBATS', 'VAR'])
            else:
                model = random.choice(['ARIMA', 'GARCH'])
    return model


