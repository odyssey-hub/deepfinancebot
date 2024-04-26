import os
import datetime as dt
from app import project_dir
from chatbot.helpers.ParamHelpers.ParamParser import ParamParser
from finance.FinTimeSeries import FinTimeSeries


class ParamHelper:

    @classmethod
    def ts_from_param_period(cls, ticker, timeframe, param_period, curr_date=dt.date.today(),
                             include_today=False, from_db=True):
        if len(param_period) == 1:
            period = param_period[0]
            period_type, period_num = ParamParser.extract_period_num_and_type(period)
            return FinTimeSeries.from_last(ticker, period_type, period_num, timeframe, curr_date,
                                           include_today, from_db)
        else:
            start = param_period[0]
            end = param_period[1]
            return FinTimeSeries(ticker, timeframe, start, end, from_db)


    @classmethod
    def load_help_file(cls, cmd):
        path = os.path.join(project_dir, 'help', 'cmds', f'{cmd}.txt')
        with open(path, 'r', encoding='UTF-8') as file:
            help_message = file.read()
        return help_message








