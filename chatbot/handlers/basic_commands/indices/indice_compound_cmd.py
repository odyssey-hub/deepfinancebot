import argparse
import logging

from tabulate import tabulate

from app import bot
from chatbot.helpers.ParamHelpers.ParamHelper import ParamHelper
from chatbot.helpers.ParamHelpers.ParamParser import ParamParser
from chatbot.handlers.basic_commands.indices.indice_compound_query import indice_compound
from finance.exceptions.MoexExceptions import RequestException

indice_compound_commands = ['index', 'indice']


@bot.message_handler(commands=indice_compound_commands)
def indice_compound_handler(user_message):
    params_dict = ParamParser.get_params_dict(user_message, parse_cmd)
    if params_dict is None:
        return

    if params_dict['help']:
        bot.send_message(user_message.chat.id, ParamHelper.load_help_file('index'))
        return

    bot_message, error = execute_command(params_dict)

    output_bot_message(user_message.chat.id, bot_message, error)


def parse_cmd(user_params_str: str):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('indice_name', default=None)
    return ParamParser.parse_params_str(user_params_str, parser)


def execute_command(params_dict):
    error = True

    try:
        bot_message = indice_compound(params_dict)
    except RequestException as e:
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
        table = '<pre>' + tabulate(bot_message, headers='keys') + '</pre>'
        bot.send_message(chat_id,  table, parse_mode='HTML')







