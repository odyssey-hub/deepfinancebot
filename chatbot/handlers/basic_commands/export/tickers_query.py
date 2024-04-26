import os

from app import project_dir
from chatbot.db.Tickers import Tickers
from chatbot.exceptions.DBException import DBException
from finance.FinTimeSeries import FinTimeSeries
from finance.MoexAPI import MoexAPI


def tickers(params_dict):
    #ticker = params_dict['ticker']
    is_cmd_list = params_dict['list']
    is_cmd_cnt = params_dict['cnt']
    cmd_ticker = params_dict['info']


    if cmd_ticker:
        return get_ticker_info(cmd_ticker)
    # elif ticker:
    #     return get_ticker_info(ticker)
    elif is_cmd_list:
        return ticker_list()
    elif is_cmd_cnt:
        return tickers_cnt()
    else:
        return tickers_cnt()


def get_ticker_info(ticker):
    if ticker[0] != '.':
        last_date = MoexAPI.get_ticker_last_date(ticker)
    else:
        last_date = MoexAPI.get_ticker_last_date(ticker, market='index')
    text_info = f"Тикер {ticker} поддерживается, последние данные: {last_date}\n"

    try:
        ticker_ts = FinTimeSeries.from_last(ticker, 'y', 1, 24, include_today=True)
        text_info += create_ticker_info(ticker, ticker_ts)
    except DBException:
        pass

    return text_info


def calc_change(ticker, timeframe: int):
    ticker_ts = FinTimeSeries.from_last(ticker, 'y', 1, timeframe, include_today=True)
    return ticker_ts.last_change()


def create_sentence_change(abs_chg, percent_chg, change_period: str):
    if abs_chg >= 0:
        return f"Изм. {change_period}: +{round(abs_chg, 3)} (+{round(percent_chg, 3)}%) ↗\n"
    else:
        return f"Изм. {change_period}: {round(abs_chg, 3)} ({round(percent_chg, 3)}%) ↘\n"


def create_ticker_info(ticker, ticker_ts):
    last_record = ticker_ts.last_record()
    last_db_date = last_record['begin']
    #text_info = f"Дата последней записи в БД: {last_db_date[:10]}\n"
    text_info = f"Посл. Close: {last_record['close']}\n"
    text_info += f"Посл. Open: {last_record['open']}\n"
    text_info += f"Посл. Low: {last_record['low']}\n"
    text_info += f"Посл. High: {last_record['high']}\n"
    text_info += f"Посл. Volume: {last_record['volume']}\n"

    abs_chg, percent_chg = ticker_ts.last_change()
    text_info += create_sentence_change(abs_chg, percent_chg, 'день')
    abs_chg, percent_chg = calc_change(ticker, 7)
    text_info += create_sentence_change(abs_chg, percent_chg, 'неделя')
    abs_chg, percent_chg = calc_change(ticker, 31)
    text_info += create_sentence_change(abs_chg, percent_chg, 'месяц')
    abs_chg, percent_chg = calc_change(ticker, 4)
    text_info += create_sentence_change(abs_chg, percent_chg, 'квартал')
    abs_chg, percent_chg = ticker_ts.full_change()
    text_info += create_sentence_change(abs_chg, percent_chg, 'год')

    return text_info


def ticker_list():
    filename = 'tickers_big.txt'
    path = os.path.join(project_dir, 'chatbot', 'db', 'tickers', filename)
    return path


def tickers_cnt():
    return len(Tickers.get_tickers())
