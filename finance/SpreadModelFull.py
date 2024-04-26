import numpy as np
import pandas as pd
import datetime as dt
from itertools import combinations
from math import isnan
from finance.FinTimeSeries import FinTimeSeries
from finance.FinTSComparator import FinTSComparator
from app import bot


class SpreadModelFull:
    stop = False

    def __init__(self, tickers, interval, corr, diff, return_stats=False, curr_date=dt.date.today()):
        self.tickers = tickers
        self.interval = interval
        self.corr = corr
        self.diff = diff
        self.return_stats = return_stats
        self.current_date = curr_date

        self._ts_dict = dict()
        self._ts_deltas = dict()
        self._ts_avgrs = dict()

    def run(self):
        self.__prepare_data()

        recommended_pairs = []
        tickers_combinations = list(combinations(self.tickers, 2))

        for tickers_pair in tickers_combinations:
            if SpreadModelFull.stop:
                break

            ticker1, ticker2 = tickers_pair[0], tickers_pair[1]
            ts1, ts2 = self._ts_dict[ticker1], self._ts_dict[ticker2]

            corr = ts1.data['close'].tail(self.interval).corr(ts2.data['close'].tail(self.interval))
            if corr < self.corr or isnan(corr):
                continue

            last_day = self.__calculate(ts1, ts2)
            diff = last_day.tolist()[0]
            if diff >= self.diff:
                if self.return_stats:
                    tickers_pair = (ticker1, ticker2, corr, diff)
                else:
                    tickers_pair = (ticker1, ticker2)
                recommended_pairs.append(tickers_pair)

        self.__clean_data()
        return recommended_pairs



    def _preload_tickers(self):
        for ticker in self.tickers:
            ts = FinTimeSeries.from_trade_days(ticker, self.interval * 3,
                                               curr_date=self.current_date)
            self._ts_dict[ticker] = ts

    def _equalize_tickers(self):
        for tickers_pair in list(combinations(self.tickers, 2)):
            ticker1, ticker2 = tickers_pair[0], tickers_pair[1]
            ts1, ts2 = self._ts_dict[ticker1], self._ts_dict[ticker2]
            if not FinTSComparator.is_dates_equal(ts1.column('begin'), ts2.column('begin')):
                ts1, ts2 = FinTSComparator.equalize(ts1, ts2)
            self._ts_dict[ticker1], self._ts_dict[ticker2] = ts1, ts2

    def __calculate_deltas(self):
        for ticker in self.tickers:
            ts = self._ts_dict[ticker]
            delta = self._delta(ts.column('close'))
            self._ts_deltas[ticker] = delta
            self._ts_avgrs[ticker] = self._avrg(delta)

    def __prepare_data(self):
        self._preload_tickers()
        self._equalize_tickers()
        self.__calculate_deltas()


    def __calculate(self, ts1, ts2):
        ts = pd.DataFrame()
        ticker1, ticker2 = ts1.ticker, ts2.ticker
        ts['varios'] = self._varios(self._ts_avgrs[ticker1], self._ts_avgrs[ticker2])
        ts['median'] = self._median(ts['varios'])
        ts['abs'] = self._abs_diff(ts['varios'], ts['median'])

        return ts.tail(1)['abs']

    def __clean_data(self):
        self._ts_dict = dict()
        self._ts_deltas = dict()
        self._ts_avgrs = dict()

    def _delta(self, ts_close):
        return ts_close.pct_change(self.interval - 1) * 100

    def _avrg(self, ts_delta):
        ts = pd.DataFrame()
        ts['delta'] = ts_delta
        ts['avrg'] = np.NAN
        n = len(ts_delta)
        per = self.interval
        for i in range(n - 1, 0, -1):
            left = i - per + 1
            ts['avrg'][i] = ts['delta'][left:i + 1].sum(min_count=per) / per
        return ts['avrg']

    def _varios(self, ts1_avrg, ts2_avrg):
        return ts1_avrg - ts2_avrg

    def _median(self, ts_varios):
        ts = pd.DataFrame()
        ts['varios'] = ts_varios
        ts['median'] = np.NAN
        n = len(ts_varios)
        per = self.interval
        for i in range(n - 1, 0, -1):
            left = i - per + 1
            right = i + 1
            if np.isnan(ts['varios'][left]):
                break
            ts['median'][i] = ts['varios'][left:right].median()
        return ts['median']

    def _abs_diff(self, ts_varios, ts_median):
        return np.abs(ts_varios - ts_median)

    def _tickers_corr(self, ts1, ts2):
        ts1.data, ts2.data = ts1.data.tail(self.interval), ts2.data.tail(self.interval)
        return ts1.column('close').corr(ts2.column('close'))











    # def __output_progress(self, i, chat_id, combinations_num, recommended_num):
    #     mess = ''
    #     if i == (combinations_num // 4):
    #         mess = f'[|||||...............] {(combinations_num // 4)}/{combinations_num} \n'
    #     elif i == (combinations_num // 2):
    #         mess = f'[||||||||||..........] {(combinations_num // 2)}/{combinations_num} \n'
    #     else:
    #         mess = f'[|||||||||||||||.....] {(combinations_num * 3 // 4)}/{combinations_num} \n'
    #     mess += f'Кол-во найденных пар: {recommended_num}'
    #     bot.send_message(chat_id, mess)


    # def run_bot(self, chat_id):
    #     bot.send_message(chat_id, 'Предобработка данных.....')
    #     self.__prepare_data()
    #
    #     recommended_pairs = []
    #     tickers_combinations = list(combinations(self.tickers, 2))
    #     combinations_num = len(tickers_combinations)
    #     i = 0
    #     progress_low = combinations_num // 4
    #     progress_half = combinations_num // 2
    #     progress_upper = combinations_num * 3 // 4
    #     bot.send_message(chat_id, f'Всего пар: {combinations_num}, провожу поиск, займет время.....')
    #
    #     for tickers_pair in tickers_combinations:
    #         if SpreadModelFull.stop:
    #             break
    #
    #         if i == progress_low or i == progress_half or i == progress_upper:
    #             self.__output_progress(i, chat_id, combinations_num, len(recommended_pairs))
    #         i = i + 1
    #
    #         ticker1, ticker2 = tickers_pair[0], tickers_pair[1]
    #         ts1, ts2 = self._ts_dict[ticker1], self._ts_dict[ticker2]
    #
    #         corr = ts1.data['close'].tail(self.interval).corr(ts2.data['close'].tail(self.interval))
    #         if corr < self.corr:
    #             continue
    #
    #         last_day = self.__calculate(ts1, ts2)
    #         diff = last_day.tolist()[0]
    #         if diff >= self.diff:
    #             tickers_pair = (ticker1, ticker2, corr, diff)
    #             recommended_pairs.append(tickers_pair)
    #
    #
    #
    #     self.__clean_data()
    #     bot.send_message(chat_id, f'Поиск завершен, найдено {len(recommended_pairs)} пар. Подготовка результатов......')
    #     return recommended_pairs