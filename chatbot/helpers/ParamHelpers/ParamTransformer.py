import re

from finance.FinTimeSeries import FinTimeSeries


class ParamTransformer:

    @classmethod
    def transform_timeframe_period(cls, timeframe, period):
        timeframe = FinTimeSeries.transform_timeframe_for_api(timeframe)
        if len(period) == 2:
            period = cls.reverse_period_dates(period)
        return timeframe, period

    @classmethod
    def reverse_period_dates(cls, period_dates):
        start = cls.reverse_date(period_dates[0])
        end = cls.reverse_date(period_dates[1])
        return [start, end]

    @staticmethod
    def reverse_date(date):
        reversed_date_pattern = re.compile(r"^(\d{2})[.-](\d{2})[.-](\d{4})$")
        if re.fullmatch(reversed_date_pattern, date):
            matches = re.findall(reversed_date_pattern, date)
            day = matches[0][0]
            month = matches[0][1]
            year = matches[0][2]
            reversed_date = f"{year}.{month}.{day}"
            return reversed_date
        else:
            return date