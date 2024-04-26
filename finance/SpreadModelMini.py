import os
import pandas as pd
import datetime as dt
from itertools import combinations

from app import project_dir
from finance.SpreadModelFull import SpreadModelFull


class SpreadModelMini(SpreadModelFull):

    def __init__(self, tickers, interval, corr, diff, curr_date=dt.date.today()):
        super().__init__(tickers, interval, corr, diff, curr_date)
        self.export_path = ""

    def run(self, export_results=False):
        self.__prepare_data()
        recommended_pairs = []
        ticker_combinations = list(combinations(self.tickers, 2))
        for tickers_pair in ticker_combinations:
            ticker1, ticker2 = tickers_pair[0], tickers_pair[1]
            ts1, ts2 = self._ts_dict[ticker1], self._ts_dict[ticker2]

            result = self.__calculate(ts1, ts2)
            last_day = result.tail(1)
            corr = ts1.data['close'].tail(self.interval).corr(ts2.data['close'].tail(self.interval))
            diff = last_day['abs'].tolist()[0]
            if diff >= self.diff and corr >= self.corr:
                tickers_pair = list(tickers_pair)
                tickers_pair.append(corr)
                tickers_pair.append(diff)
                recommended_pairs.append(tickers_pair)

            if export_results and len(self.tickers) == 2:
                self.export_path = self.export_xlsx(result, ticker1, ticker2)
        return recommended_pairs

    def export_xlsx(self, df: pd.DataFrame, ticker1: str, ticker2: str):
        #project_dir = os.path.dirname(os.path.dirname(__file__))
        filename = ticker1 + "_" + ticker2 + "_" + dt.datetime.now().strftime("%d.%m.%Y_%H.%M.%S") + '.xlsx'
        path = os.path.join(project_dir, 'data', 'export', 'model', 'mini', filename)
        df.to_excel(path, index=False)
        return path

    def __prepare_data(self):
        self._preload_tickers()
        self._equalize_tickers()

    def __calculate(self, ts1, ts2):
        ts = pd.DataFrame()
        ticker1, ticker2 = ts1.ticker, ts2.ticker
        ts['date'] = ts1.column('begin')
        ts[ticker1 + '_close'], ts[ticker2 + '_close'] = ts1.column('close'), ts2.column('close')
        ts[ticker1 + '_delta'] = self._delta(ts[ticker1 + '_close'])
        ts[ticker2 + '_delta'] = self._delta(ts[ticker2 + '_close'])
        ts[ticker1 + '_avrg'] = self._avrg(ts[ticker1 + '_delta'])
        ts[ticker2 + '_avrg'] = self._avrg(ts[ticker2 + '_delta'])
        ts['varios'] = self._varios(ts[ticker1 + '_avrg'], ts[ticker2 + '_avrg'])
        ts['median'] = self._median(ts['varios'])
        ts['abs'] = self._abs_diff(ts['varios'], ts['median'])
        return ts


