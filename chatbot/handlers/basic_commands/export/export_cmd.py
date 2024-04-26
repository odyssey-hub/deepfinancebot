import argparse
import logging

from app import bot
from chatbot.exceptions.DBException import DBException
from chatbot.exceptions.ParamException import ParamException
from chatbot.helpers.ParamHelpers.ParamHelper import ParamHelper
from chatbot.helpers.ParamHelpers.ParamParser import ParamParser
from finance.exceptions.MoexExceptions import *
from chatbot.handlers.basic_commands.export.export_query import export

export_commands = ['export']


@bot.message_handler(commands=export_commands)
def export_cmd_handler(user_message):
    params_dict = ParamParser.get_params_dict(user_message, parse_cmd)
    if params_dict is None:
        return

    if params_dict['help']:
        bot.send_message(user_message.chat.id, ParamHelper.load_help_file('export'))
        return

    bot_message, error = execute_command(params_dict)

    output_bot_message(user_message.chat.id, bot_message, error)


def parse_cmd(user_params_str: str):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('ticker', default=None)
    parser.add_argument('-p', '--period', nargs='+', default=None, type=str.lower)
    parser.add_argument('-t', '--timeframe', default='d', type=str.lower)

    return ParamParser.parse_params_str(user_params_str, parser)


def execute_command(params_dict):
    error = True

    try:
        bot_message = export(params_dict)
    except (ParamException, RequestException, DBException) as e:
        bot_message = e.message
    except Exception as e:
        bot_message = "Неизвестная ошибка"
        logging.exception(e)
    else:
        error = False

    return bot_message, error


def output_bot_message(chat_id, bot_message, error):
    if error:
        bot.send_message(chat_id, bot_message)
    else:
        path = bot_message
        doc = open(path, 'rb')
        bot.send_document(chat_id, doc)
