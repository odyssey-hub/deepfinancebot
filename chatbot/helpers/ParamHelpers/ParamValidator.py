import re
from chatbot.helpers.ParamHelpers.ParamParser import ParamParser


class ParamValidator:

    TIMEFRAMES = ('10min', 'h', 'd', 'w', 'm', 'q')
    COLUMNS = ('begin', 'open', 'high', 'low', 'close', 'volume')

    MAX_DAYS = 1500
    MAX_WEEKS = 300
    MAX_MONTHS = 60
    MAX_YEARS = 6

    @classmethod
    def is_correct_timeframe(cls, timeframe):
        if timeframe in cls.TIMEFRAMES:
            return True
        else:
            return False

    @classmethod
    def is_correct_columns(cls, columns):
        if columns is None:
            return True
        for column in columns:
            if column not in cls.COLUMNS:
                return False
        return True

    @classmethod
    def is_correct_column(cls, column):
        return column in cls.COLUMNS

    @classmethod
    def is_correct_period(cls, period):
        if len(period) == 1:
            period = period[0]
            period_last_pattern = re.compile(r"^(\d{1,3})([dwmy])$")
            if re.fullmatch(period_last_pattern, period):
                period_type, period_num = ParamParser.extract_period_num_and_type(period)
                if period_type == 'd':
                    if period_num < 2:
                        return False
                    else:
                        return True
                elif period_type == 'w' and period_num > cls.MAX_WEEKS or period_num == 0:
                    return False
                elif period_type == 'm' and period_num > cls.MAX_MONTHS:
                    return False
                elif period_type == 'y' and period_num > cls.MAX_YEARS:
                    return False
                else:
                    return True
            else:
                return False
        elif len(period) == 2:
            period_from = period[0]
            period_to = period[1]
            if len(period_from) != 10 or len(period_to) != 10:
                return False
            date_pattern = re.compile(r"^\d{2,4}[.-][0-1][0-9][.-](\d){2,4}$")
            if re.fullmatch(date_pattern, period_from) and re.fullmatch(date_pattern, period_to):
                return True
            else:
                return False
        else:
            return False







