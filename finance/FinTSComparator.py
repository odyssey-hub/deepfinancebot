from finance.FinTimeSeries import FinTimeSeries
import pandas as pd
import datetime as dt

from finance.exceptions.MoexExceptions import RequestException


class FinTSComparator:

    @classmethod
    def corr(cls, tickers, period_type, period_num, timeframe, column='close',
             start='2020-01-01', end='2024-01-01', curr_date=dt.date.today()):
        timeseries = []

        for ticker in tickers:
            if period_type == 'p':
                ticker_ts = FinTimeSeries(ticker, timeframe, start, end)
            else:
                ticker_ts = FinTimeSeries.from_last(ticker, period_type, period_num, timeframe, curr_date)
            if ticker_ts.is_empty():
                raise RequestException("ticker")
            timeseries.append(ticker_ts)

        timeseries = cls.equalize_many(timeseries)

        if len(timeseries) == 2:
            ticker1_column, ticker2_column = timeseries[0].column(column), timeseries[1].column(column)
            return ticker1_column.corr(ticker2_column)

        elif len(tickers) > 2:
            df_tickers = pd.DataFrame()
            for ts in timeseries:
                ticker = ts.ticker
                df_tickers[ticker] = ts.column(column)
            return df_tickers.corr()


    @staticmethod
    def is_dates_equal(ts1_dates, ts2_dates):
        if len(ts1_dates) != len(ts2_dates):
            return False
        return set(ts1_dates) == set(ts2_dates)

    @staticmethod
    def equalize(ts1: FinTimeSeries, ts2: FinTimeSeries, method='fill'):
        dates_ts1, dates_ts2 = set(ts1.column('begin')), set(ts2.column('begin'))
        ts1_skips, ts2_skips = list(dates_ts2 - dates_ts1), list(dates_ts1 - dates_ts2)
        if len(ts1_skips) > 0:
            if method == 'fill':
                insert_df = pd.DataFrame()
                insert_df['begin'] = ts1_skips
                ts1.data = pd.concat([ts1.data, insert_df], ignore_index=True).sort_values('begin', ignore_index=True)
                ts1.fill_na()
            else:
                ts2.data = ts2.data.loc[~ts2.data['begin'].isin(ts1_skips)]
                ts2.data.reset_index(drop=True, inplace=True)
        if len(ts2_skips) > 0:
            if method == 'fill':
                insert_df = pd.DataFrame()
                insert_df['begin'] = ts2_skips
                ts2.data = pd.concat([ts2.data, insert_df], ignore_index=True).sort_values('begin', ignore_index=True)
                ts2.fill_na()
            else:
                ts1.data = ts1.data.loc[~ts1.data['begin'].isin(ts2_skips)]
                ts1.data.reset_index(drop=True, inplace=True)
        return ts1, ts2

    @classmethod
    def equalize_many(cls, ts_arr, method='drop'):
        n = len(ts_arr)
        for i in range(0, n):
            for j in range(i+1, n):
                ts1, ts2 = ts_arr[i], ts_arr[j]
                if not cls.is_dates_equal(ts1.column('begin'), ts2.column('begin')):
                    ts_arr[i], ts_arr[j] = cls.equalize(ts1, ts2, method=method)
        return ts_arr



