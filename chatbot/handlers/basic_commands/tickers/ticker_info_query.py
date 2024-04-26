from chatbot.exceptions.DBException import DBException
from finance.FinTimeSeries import FinTimeSeries
from finance.MoexAPI import MoexAPI


def ticker_info(params_dict):
    ticker = params_dict['ticker']

    if ticker:
        return get_ticker_info(ticker)

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
