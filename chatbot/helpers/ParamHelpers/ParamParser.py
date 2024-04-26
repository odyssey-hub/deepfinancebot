import argparse
import re
import shlex

from app import bot
from chatbot.exceptions.ParamException import ParamException


class ParamParser:

    @staticmethod
    def parse_params_str(user_params_str, parser: argparse.ArgumentParser):
        try:
            parser.add_argument('-h', '--help', action='store_true')
            args = parser.parse_args(shlex.split(user_params_str))
            args_dict = args.__dict__
            return args_dict
        except Exception as e:
            raise ParamException("no_param")
        except SystemExit:
            raise ParamException("argparse")

    @staticmethod
    def get_params_dict(user_message, parse_cmd):
        try:
            user_params_str = user_message.text.split(maxsplit=1)[1]
        except IndexError:
            return {'help': True}

        if user_params_str == '-h':
            return {'help': True}

        try:
            params_dict = parse_cmd(user_params_str)
        except ParamException:
            bot_message = 'Ошибка. Указаны неверные параметры или их значения'
            bot.send_message(user_message.chat.id, bot_message)
            return None

        return params_dict

    @staticmethod
    def extract_period_num_and_type(period):
        period_last_pattern = re.compile(r"^(\d{1,3})([dwmy])$")
        matches = re.findall(period_last_pattern, period)
        period_num = matches[0][0]
        period_type = matches[0][1]
        return period_type, int(period_num)
