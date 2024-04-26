import logging

from app import bot
from chatbot.exceptions.DBException import DBException
from chatbot.exceptions.ParamException import ParamException
from chatbot.helpers.ParamHelpers.ParamHelper import ParamHelper
from chatbot.helpers.ParamHelpers.ParamParser import ParamParser
from chatbot.handlers.additional_commands.chart.chart_query import chart
from finance.exceptions.MoexExceptions import *
import argparse

chart_commands = ['chart']


@bot.message_handler(commands=chart_commands)
def chart_cmd_handler(user_message):
    params_dict = ParamParser.get_params_dict(user_message, parse_cmd)
    if params_dict is None:
        return

    if params_dict['help']:
        bot.send_message(user_message.chat.id, ParamHelper.load_help_file('chart'))
        return

    bot_message, error = execute_command(params_dict)

    output_bot_message(user_message.chat.id, bot_message, error, params_dict['is_image'])


def parse_cmd(user_params_str: str):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('tickers', nargs='+', default=None)
    parser.add_argument('-p', '--period', nargs='+', default=None, type=str.lower)
    parser.add_argument('-t', '--timeframe', default='d', type=str.lower)
    parser.add_argument('-c', '--column', default='close', type=str.lower)
    parser.add_argument('-candles', '--is_candles_chart', action='store_true')
    parser.add_argument('-img', '--is_image', action='store_true')
    return ParamParser.parse_params_str(user_params_str, parser)


def execute_command(params_dict):
    error = True

    try:
        bot_message = chart(params_dict)
    except (ParamException, RequestException, DBException) as e:
        bot_message = e.message
    except Exception as e:
        bot_message = "Неизвестная ошибка"
        logging.exception(e)
    else:
        error = False

    return bot_message, error


def output_bot_message(chat_id, bot_message, error, is_image):
    if error:
        bot.send_message(chat_id, bot_message)
    elif not is_image:
        path = bot_message
        doc = open(path, 'rb')
        bot.send_document(chat_id, doc)
    else:
        path = bot_message
        doc = open(path, 'rb')
        bot.send_photo(chat_id, doc)

