import argparse
import logging

from app import bot
from chatbot.exceptions.DBException import DBException
from chatbot.exceptions.Delta2WException import Delta2WException
from chatbot.exceptions.ParamException import ParamException
from chatbot.helpers.ParamHelpers.ParamHelper import ParamHelper
from chatbot.helpers.ParamHelpers.ParamParser import ParamParser
from chatbot.handlers.delta2w.delta2w_min_query import delta2w
from finance.exceptions.MoexExceptions import *


model_commands = ['model', 'delta2w']


@bot.message_handler(commands=model_commands)
def delta2w_handler(user_message):
    params_dict = ParamParser.get_params_dict(user_message, parse_cmd)
    if params_dict is None:
        return

    if params_dict['help']:
        bot.send_message(user_message.chat.id, ParamHelper.load_help_file('delta2w'))
        return

    bot.send_message(user_message.chat.id, 'Подождите, обработка займет время.....')
    bot_message, export_path, error = execute_command(params_dict)

    output_bot_message(user_message.chat.id, bot_message, export_path, error)


def parse_cmd(user_params_str: str):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('tickers', nargs='+', default=None)
    parser.add_argument('-per', '--interval', default=20)
    parser.add_argument('-corr', '--corr', default=0.85)
    parser.add_argument('-diff', '--diff', default=10)
    parser.add_argument('-export', '--export', action='store_true')
    return ParamParser.parse_params_str(user_params_str, parser)


def execute_command(params_dict):
    error = True
    export_path = ""

    try:
        bot_message, export_path = delta2w(params_dict)
    except (ParamException, RequestException, Delta2WException, DBException) as e:
        bot_message = e.message
    except Exception as e:
        bot_message = "Ошибка. Неизвестная ошибка"
        logging.exception(e)
    else:
        error = False

    return bot_message, export_path, error


def output_bot_message(chat_id, bot_message, export_path, error):
    if error:
        bot.send_message(chat_id, bot_message)
    else:
        recommended_pairs = bot_message
        message = 'Нет рекомендаций'
        if recommended_pairs:
            message = f'Обнаружено {len(recommended_pairs)} рекомендованных пар: \n'
            for pair in recommended_pairs:
                message += f"{pair[0]}  {pair[1]}   {round(pair[2], 3) }   {round(pair[3], 3)}\n"
        bot.send_message(chat_id, message)
        if export_path:
            doc = open(export_path, 'rb')
            bot.send_document(chat_id, doc)








