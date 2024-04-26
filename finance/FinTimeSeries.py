import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import datetime as dt
import os
from dateutil.relativedelta import relativedelta

from app import db, project_dir
from chatbot.exceptions.DBException import DBException
from finance.MoexAPI import MoexAPI


class FinTimeSeries:

    STD_COLUMNS = ('begin', 'open', 'high', 'low', 'close', 'volume')
    FROM_DB = True


    def __init__(self, ticker, timeframe, start, end, from_db=FROM_DB):
        if ticker[0] != '.':
            market = 'shares'
        else:
            ticker = ticker[1:]
            market = 'index'

        if timeframe == 24 and market == 'shares' and from_db:
            try:
                data = db.read_ts(ticker, timeframe, start, end)
            except Exception:
                raise DBException("ticker", ticker)
        else:
            data = MoexAPI.download_history_data(ticker, timeframe, start, end, self.STD_COLUMNS, market)
            data = pd.DataFrame(data)

        self.data = data
        self.ticker = ticker
        self.timeframe = timeframe
        self.start = start
        self.end = end

    @classmethod
    def from_trade_days(cls, ticker, num_last_days, timeframe=24, curr_date=dt.date.today(),
                        include_today=False, from_db=FROM_DB):
        start = curr_date - relativedelta(days=num_last_days*2)
        if include_today:
            end = curr_date
        else:
            yesterday = curr_date - dt.timedelta(days=1)
            end = yesterday

        ts = cls(ticker, 24, str(start), str(end), from_db)
        ts.data = ts.data.tail(num_last_days)
        ts.data = ts.data.reset_index(drop=True)

        if timeframe != 24: # -p 30d -t h
            start = ts.data['begin'].iloc[0]
            end = cls.add_delta(ts.data['begin'].iloc[-1], delta_duration=1, delta_mode='d')
            ts = cls(ticker, timeframe, start, end, from_db)

        return ts

    @classmethod
    def from_weeks(cls, ticker, num_weeks, timeframe=24, curr_date=dt.date.today(),
                   include_today=False, from_db=FROM_DB):
        start = curr_date - dt.timedelta(weeks=num_weeks)
        if include_today:
            end = curr_date
        else:
            end = curr_date - dt.timedelta(days=1)
        return cls(ticker, timeframe, str(start), str(end), from_db)

    @classmethod
    def from_months(cls, ticker, num_months, timeframe=24, curr_date=dt.date.today(),
                    include_today=False, from_db=FROM_DB):
        start = curr_date - relativedelta(months=num_months)
        if include_today:
            end = curr_date
        else:
            end = curr_date - dt.timedelta(days=1)
        return cls(ticker, timeframe, str(start), str(end), from_db)

    @classmethod
    def from_years(cls, ticker, num_years, timeframe=24, curr_date=dt.date.today(),
                   include_today=False, from_db=FROM_DB):
        start = curr_date - relativedelta(years=num_years)
        if include_today:
            end = curr_date
        else:
            end = curr_date - dt.timedelta(days=1)
        return cls(ticker, timeframe, str(start), str(end), from_db)

    @classmethod
    def from_last(cls, ticker, period_type, period_num, timeframe, curr_date=dt.date.today(),
                  include_today=False, from_db=FROM_DB):
        if period_type == 'd':
            return cls.from_trade_days(ticker, period_num, timeframe, curr_date, include_today, from_db)
        elif period_type == 'w':
            return cls.from_weeks(ticker, period_num, timeframe, curr_date, include_today, from_db)
        elif period_type == 'm':
            return cls.from_months(ticker, period_num, timeframe, curr_date, include_today, from_db)
        elif period_type == 'y':
            return cls.from_years(ticker, period_num, timeframe, curr_date, include_today, from_db)
        else:
            return cls.from_trade_days(ticker, period_num, timeframe, curr_date, include_today, from_db)

    def column(self, name):
        return self.data[name]

    def columns(self, column_names):
        return self.data[column_names]

    def last_record(self):
        return self.data.iloc[-1]

    def last_price(self):
        return self.data['close'].iloc[-1]

    def last_change(self):
        abs_change = self.data['close'].iloc[-1] - self.data['close'].iloc[-2]
        percent_change = (abs_change / self.data['close'].iloc[-2]) * 100
        return abs_change, percent_change

    def full_change(self):
        abs_change = self.data['close'].iloc[-1] - self.data['close'].iloc[0]
        percent_change = (abs_change / self.data['close'].iloc[0]) * 100
        return abs_change, percent_change

    def candle_chart(self, without_slider=True):
        fig = go.Figure(data=[go.Candlestick(x=self.data['begin'],
                                             open=self.data['open'],
                                             high=self.data['high'],
                                             low=self.data['low'],
                                             close=self.data['close'])])
        if without_slider:
            fig.update_layout(xaxis_rangeslider_visible=False)
        fig.show()

    def line_chart(self, column='close', with_slider=False):
        fig = px.line(self.data, x='begin', y=column)
        if with_slider:
            fig.update_xaxes(rangeslider_visible=True)
        fig.show()

    def mean(self, column='close'):
        return self.data[column].mean()

    def var(self, column='close'):
        return self.data[column].var()

    def median(self, column='close'):
        return self.data[column].median()

    def std(self, column='close'):
        return self.data[column].std()

    def corr(self, columns=STD_COLUMNS):
        if len(columns) == 2:
            df_column1, df_column2 = self.data[columns[0]], self.data[columns[1]]
            return df_column1.corr(df_column2)
        elif len(columns) > 2:
            df = self.data[list(columns[1:])]
            return df.corr()
        else:
            return None

    def export_csv(self):
        #project_dir = os.path.dirname(os.path.dirname(__file__))
        filename = self.ticker+'_'+dt.datetime.now().strftime("%d.%m.%Y_%H.%M.%S")+'.csv'
        path = os.path.join(project_dir, 'data', 'export', 'tickers', filename)
        self.data.to_csv(path, index=False)
        return path

    def export_xlsx(self):
        #project_dir = os.path.dirname(os.path.dirname(__file__))
        filename = self.ticker+'_'+dt.datetime.now().strftime("%d.%m.%Y_%H.%M.%S")+'.xlsx'
        path = os.path.join(project_dir, 'data', 'export', 'tickers', filename)
        self.data.to_excel(path, index=False)
        return path

    def has_nulls(self):
        return self.nulls_count() > 0

    def nulls_count(self, by_columns=False):
        if by_columns:
            return dict(self.data.isna().sum())
        else:
            return self.data.isna().sum().sum()

    def fill_na(self, method='bfill'):
        self.data.fillna(method=method, inplace=True)

    def drop_na(self):
        self.data.dropna(inplace=True)

    def is_empty(self):
        return self.data.empty

    @staticmethod
    def add_delta(date: str, delta_duration, delta_mode='d', sub=False):
        if delta_mode == 'd':
            delta = dt.timedelta(days=delta_duration)
        elif delta_mode == 'w':
            delta = dt.timedelta(weeks=delta_duration)
        elif delta_mode == 'm':
            delta = relativedelta(months=delta_duration)
        elif delta_mode == 'y':
            delta = relativedelta(years=delta_duration)
        else:
            delta = dt.timedelta(days=delta_duration)

        dt_date = dt.date.fromisoformat(date.split(' ')[0])
        if not sub:
            date = dt_date + delta
        else:
            date = dt_date - delta

        return str(date)

    @staticmethod
    def transform_timeframe_for_api(timeframe):
        if timeframe == 'd':
            return 24
        elif timeframe == 'w':
            return 7
        elif timeframe == 'm':
            return 31
        elif timeframe == 'h':
            return 60
        elif timeframe == '10min':
            return 10
        elif timeframe == '1min':
            return 1
        else:
            return 24

    def __str__(self):
        return self.data.to_string()

    def __len__(self):
        return len(self.data['close'])

