import sqlite3
import pandas as pd
import datetime as dt

from chatbot.db.Tickers import Tickers
from finance.MoexAPI import MoexAPI
from finance.exceptions.MoexExceptions import RequestException


class DB:

    STD_COLUMNS = ['begin', 'open', 'high', 'low', 'close', 'volume']

    def __init__(self, db_path):
        try:
            self.db_conn = sqlite3.connect(db_path, check_same_thread=False)
        except Exception:
            print("Не удалось соединиться с БД")


    def read_ts(self, ticker, timeframe, start, end):
        self.check_and_update(ticker, timeframe)

        if '.' in start:
            start, end = start.replace('.', '-'), end.replace('.', '-')

        params = {'timeframe': self.detransform_timeframe(timeframe), 'start': start, 'end': end}
        query = f'SELECT * FROM "{ticker}" WHERE timeframe = :timeframe AND begin BETWEEN :start and DATETIME(:end, "+1 days") '
        df = pd.read_sql(query, con=self.db_conn, params=params)
        df = df.drop(columns=['timeframe'])

        return df

    def update_all_tickers(self, timeframe: int):
        tickers = Tickers.get_tickers()
        for ticker in tickers:
            self.check_and_update(ticker, timeframe, is_all=True)
        print("База данных успешно обновлена " + str(dt.date.today()))

    def check_and_update(self, ticker, timeframe, is_all=False):
        curr_date = dt.date.today() - dt.timedelta(days=1) #вчерашний день
        db_date = dt.date.fromisoformat(self.get_db_date(ticker, self.detransform_timeframe(timeframe))[:10])
        if db_date < curr_date:
            self.update_ticker(db_date, curr_date, ticker, timeframe, is_all)

    def update_ticker(self, db_date, curr_date, ticker, timeframe, is_all):
        start = db_date + dt.timedelta(days=1)
        end = curr_date
        try:
            new_records = MoexAPI.download_history_data(ticker, timeframe, start, end, self.STD_COLUMNS)
        except RequestException:
            print(f"Не удалось обновить тикер {ticker}")
            new_records = []
        timeframe = self.detransform_timeframe(timeframe)
        if new_records:
            new_records = pd.DataFrame(new_records)
            new_records['timeframe'] = timeframe
            new_records.to_sql(name=ticker, con=self.db_conn, index=False, if_exists='append')
        # cursor = self.db_conn.cursor()
        # timeframe = self.detransform_timeframe(timeframe)
        # query = f"INSERT INTO {ticker} {self.STD_COLUMNS.append('timeframe')} VALUES (?, ?, ?, ?, ?, ?, {timeframe}) "
        # cursor.executemany(query, new_records)
        # self.db_conn.commit()
        if not is_all:
            self.update_ticker_date(curr_date, ticker, timeframe)
        else:
            self.update_all_tickers_date(timeframe)

    def update_all_tickers_date(self, timeframe):
        cursor = self.db_conn.cursor()
        date = dt.date.today() - dt.timedelta(days=1)
        date = str(date)+' 00:00:00'
        params = (date, timeframe)
        query = "UPDATE tickers SET date = ? WHERE timeframe = ?"
        cursor.execute(query, params)
        self.db_conn.commit()

    def update_ticker_date(self, date, ticker, timeframe):
        cursor = self.db_conn.cursor()
        date = str(date)+' 00:00:00'
        params = (date, ticker, timeframe)
        query = "UPDATE tickers SET date = ? WHERE ticker = ? AND timeframe = ?"
        cursor.execute(query, params)
        self.db_conn.commit()

    def get_db_date(self, ticker, timeframe):
        cursor = self.db_conn.cursor()
        params = (ticker, timeframe)
        query = "SELECT date FROM tickers WHERE ticker = ? AND timeframe = ?"
        cursor.execute(query, params)
        db_date = cursor.fetchone()
        return db_date[0]

    @staticmethod
    def detransform_timeframe(timeframe):
        if timeframe == 24:
            return 'd'
        elif timeframe == 7:
            return 'w'
        elif timeframe == 31:
            return 'm'
        elif timeframe == 60:
            return 'h'
        elif timeframe == 10:
            return '10min'