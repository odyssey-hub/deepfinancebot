import argparse
import logging
import os

import pandas as pd
from app import bot, project_dir
from chatbot.exceptions.DBException import DBException
from chatbot.exceptions.Delta2WException import Delta2WException
from chatbot.exceptions.ParamException import ParamException
from chatbot.helpers.ParamHelpers.ParamHelper import ParamHelper
from chatbot.helpers.ParamHelpers.ParamParser import ParamParser
from finance.SpreadModelFull import SpreadModelFull
from finance.exceptions.MoexExceptions import RequestException
from chatbot.handlers.delta2w.delta2w_full_query import delta2w_full
import datetime as dt

model_commands = ['model_full', 'delta2w_full']


@bot.message_handler(commands=model_commands)
def delta2w_full_handler(user_message):
    params_dict = ParamParser.get_params_dict(user_message, parse_cmd)

    if params_dict is None:
        return

    if params_dict['help']:
        bot.send_message(user_message.chat.id, ParamHelper.load_help_file('delta2w'))
        return

    bot_message, error = execute_command(params_dict, user_message.chat.id)

    output_bot_message(user_message.chat.id, bot_message, error)


@bot.message_handler(commands=['model_stop','delta2w_stop'])
def delta2w_stop_handler(user_message):
    SpreadModelFull.stop = True
    bot.send_message(user_message.chat.id, 'Остановка модели.....')


def parse_cmd(user_params_str: str):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-diff', '--diff', action='append')
    parser.add_argument('-per', '--interval', action='append')
    parser.add_argument('-corr', '--corr', action='append')
    parser.add_argument('-and', '-AND', '--AND', action='count')
    parser.add_argument('-or', '-OR', '--OR', action='count')
    return ParamParser.parse_params_str(user_params_str, parser)


def execute_command(params_dict, chat_id):
    error = True

    try:
        bot_message = delta2w_full(params_dict, chat_id)
    except (ParamException, RequestException, Delta2WException, DBException) as e:
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
        recommended_pairs = bot_message
        if not recommended_pairs:
            bot.send_message(chat_id, 'Нет рекомендаций')
        else:
            message = f'Обнаружено {len(recommended_pairs)} рекомендованных пар: \n'
            if len(recommended_pairs) <= 60:
                i = 0
                if len(recommended_pairs[0]) < 3:
                    for pair in recommended_pairs:
                        i = i + 1
                        message += f"{i}:  {pair[0]}  {pair[1]}\n"
                else:
                    for pair in recommended_pairs:
                        i = i + 1
                        message += f"{i}:  {pair[0]}  {pair[1]}   {round(pair[2], 3)}   {round(pair[3], 3)}\n"
                bot.send_message(chat_id, message)
            else:
                export_path = export_results_xlsx(recommended_pairs)
                doc = open(export_path, 'rb')
                bot.send_document(chat_id, doc)


def export_results_xlsx(recommended_pairs):
    if len(recommended_pairs[0]) < 3:
        df = pd.DataFrame(recommended_pairs, columns=['ticker1', 'ticker2'])
    else:
        df = pd.DataFrame(recommended_pairs, columns=['ticker1', 'ticker2', 'corr', 'diff'])
    df.index = df.index + 1
    #project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    filename = 'ModelFull' + '_' + dt.datetime.now().strftime("%d.%m.%Y_%H.%M.%S") + '.xlsx'
    path = os.path.join(project_dir, 'data', 'export', 'model', 'full', filename)
    df.to_excel(path, index=True)
    return path



# def custom_parse(message):
#     user_params = message.split()[1:]
#     params = str.lower(user_params)
#     params_dict = dict()
#     if '-help' in params:
#         params_dict['help'] = True
#         return params_dict
#     if '-run' in params:
#         params_dict['corr'] = 0.85
#         params_dict['run'] = True
#         params_dict['interval'] = 20
#         params_dict['diff'] = 10
#         return params_dict
#     if 'and' in params:
#         pass
#     else:
#
#
# def get_params(cmd_params, user_params):
#     params_dict = dict()
#     for cmd_param in cmd_params:
#         i_param = user_params.index(cmd_param)
#         param_value = user_params[i_param+1]
#         params_dict[cmd_param] = param_value
#     return params_dict

