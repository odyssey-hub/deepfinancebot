from app import bot
import argparse
import logging

from chatbot.helpers.ParamHelpers.ParamHelper import ParamHelper
from chatbot.helpers.ParamHelpers.ParamParser import ParamParser
from chatbot.handlers.basic_commands.export.tickers_query import tickers
from finance.exceptions.MoexExceptions import RequestException

tickers_commands = ['tickers']


@bot.message_handler(commands=tickers_commands)
def tickers_handler(user_message):
    params_dict = ParamParser.get_params_dict(user_message, parse_cmd)

    if params_dict is None:
        return

    if params_dict['help']:
        bot.send_message(user_message.chat.id, ParamHelper.load_help_file('tickers'))
        return

    bot_message, error = execute_command(params_dict)

    output_bot_message(user_message.chat.id, bot_message, error, params_dict)


def parse_cmd(user_params_str: str):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-list', '--list', action='store_true')
    parser.add_argument('-cnt', '--cnt', action='store_true')
    parser.add_argument('-info', '--info', default=None)
    return ParamParser.parse_params_str(user_params_str, parser)


def execute_command(params_dict):
    error = True

    try:
        bot_message = tickers(params_dict)
    except RequestException as e:
        bot_message = e.message
    except Exception as e:
        bot_message = "Неизвестная ошибка"
        logging.exception(e)
    else:
        error = False

    return bot_message, error


def output_bot_message(chat_id, bot_message, error, params_dict):
    if error:
        bot.send_message(chat_id, bot_message)
    else:
        if params_dict['info']:
            ticker_info = bot_message
            bot.send_message(chat_id, ticker_info)
        elif params_dict['list']:
            path = bot_message
            doc = open(path, 'rb')
            bot.send_document(chat_id, doc)
        else:
            tickers_num = bot_message
            message = f'Всего тикеров в БД: {tickers_num}'
            bot.send_message(chat_id, message)
