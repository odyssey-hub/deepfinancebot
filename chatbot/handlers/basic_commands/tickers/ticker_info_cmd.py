from app import bot
import argparse
import logging

from chatbot.helpers.ParamHelpers.ParamHelper import ParamHelper
from chatbot.helpers.ParamHelpers.ParamParser import ParamParser
from chatbot.handlers.basic_commands.tickers.ticker_info_query import ticker_info
from finance.exceptions.MoexExceptions import RequestException


ticker_info_commands = ['ticker']

@bot.message_handler(commands=ticker_info_commands)
def tickers_handler(user_message):
    params_dict = ParamParser.get_params_dict(user_message, parse_cmd)

    if params_dict is None:
        return

    if params_dict['help']:
        bot.send_message(user_message.chat.id, ParamHelper.load_help_file('ticker_info'))
        return

    bot_message, error = execute_command(params_dict)

    output_bot_message(user_message.chat.id, bot_message, error)


def parse_cmd(user_params_str: str):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('ticker', default=None)
    return ParamParser.parse_params_str(user_params_str, parser)


def execute_command(params_dict):
    error = True

    try:
        bot_message = ticker_info(params_dict)
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
        info = bot_message
        bot.send_message(chat_id, info)