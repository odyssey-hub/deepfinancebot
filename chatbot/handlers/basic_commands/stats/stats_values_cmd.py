import argparse
import logging

from app import bot
from chatbot.exceptions.DBException import DBException
from chatbot.exceptions.ParamException import ParamException
from chatbot.helpers.ParamHelpers.ParamHelper import ParamHelper
from chatbot.helpers.ParamHelpers.ParamParser import ParamParser
from chatbot.handlers.basic_commands.stats.stats_values_query import stats_values
from finance.exceptions.MoexExceptions import RequestException

mean_commands = ['mean', 'ma']
var_commands = ['var']
median_commands = ['median']
std_commands = ['std']


@bot.message_handler(commands=mean_commands)
def mean_handler(user_message):
    stats_values_handler('mean', user_message)


@bot.message_handler(commands=var_commands)
def var_handler(user_message):
    stats_values_handler('var', user_message)


@bot.message_handler(commands=median_commands)
def median_handler(user_message):
    stats_values_handler('median', user_message)


@bot.message_handler(commands=std_commands)
def std_handler(user_message):
    stats_values_handler('std', user_message)


def stats_values_handler(stats_value, user_message):
    params_dict = ParamParser.get_params_dict(user_message, parse_cmd)
    if params_dict is None:
        return

    if params_dict['help']:
        bot.send_message(user_message.chat.id, ParamHelper.load_help_file(stats_value))
        return

    bot_message, error = execute_command(stats_value, params_dict)

    output_bot_message(user_message.chat.id, bot_message)


def parse_cmd(user_params_str: str):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('ticker', default=None)
    parser.add_argument('-p', '--period', nargs='+', default=None, type=str.lower)
    parser.add_argument('-t', '--timeframe', default='d', type=str.lower)
    parser.add_argument('-c', '--column', default='close', type=str.lower)
    return ParamParser.parse_params_str(user_params_str, parser)


def execute_command(stats_value, params_dict):
    error = True

    try:
        bot_message = stats_values(stats_value, params_dict)
    except (ParamException, RequestException, DBException) as e:
        bot_message = e.message
    except Exception as e:
        bot_message = "Неизвестная ошибка"
        logging.exception(e)
    else:
        error = False

    return bot_message, error


def output_bot_message(chat_id, bot_message):
    bot.send_message(chat_id, bot_message)

