import logging

import pandas as pd
from tabulate import tabulate

from app import bot
from chatbot.exceptions.DBException import DBException
from chatbot.exceptions.ParamException import ParamException
from chatbot.helpers.ParamHelpers.ParamHelper import ParamHelper
from chatbot.helpers.ParamHelpers.ParamParser import ParamParser
from chatbot.handlers.basic_commands.corr.corr_query import corr

import argparse

from finance.exceptions.MoexExceptions import RequestException

corr_commands = ['corr']


@bot.message_handler(commands=corr_commands)
def corr_cmd_handler(user_message):
    params_dict = ParamParser.get_params_dict(user_message, parse_cmd)
    if params_dict is None:
        return

    if params_dict['help']:
        bot.send_message(user_message.chat.id, ParamHelper.load_help_file('corr'))
        return

    bot_message, error = execute_command(params_dict)

    output_bot_message(user_message.chat.id, bot_message)


def parse_cmd(user_params_str: str):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('tickers', nargs='+', default=None)
    parser.add_argument('-p', '--period', nargs='+', default=None, type=str.lower)
    parser.add_argument('-t', '--timeframe', default='d', type=str.lower)
    parser.add_argument('-c', '--columns', nargs='+', default=None, type=str.lower)

    return ParamParser.parse_params_str(user_params_str, parser)


def execute_command(params_dict):
    error = True

    try:
        bot_message = corr(params_dict)
    except (ParamException, RequestException, DBException) as e:
        bot_message = e.message
    except Exception as e:
        bot_message = "Неизвестная ошибка"
        logging.exception(e)
    else:
        error = False

    return bot_message, error


def output_bot_message(chat_id, bot_message):
    if type(bot_message) is pd.DataFrame:
        table = '<pre>' + tabulate(bot_message, headers='keys') + '</pre>'
        bot.send_message(chat_id,  table, parse_mode='HTML')
    else:
        bot.send_message(chat_id, bot_message)



