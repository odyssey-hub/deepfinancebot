import apimoex
import requests

from finance.exceptions.MoexExceptions import RequestException


class MoexAPI:
    ISS_URL = 'https://iss.moex.com/iss/'

    @staticmethod
    def download_history_data(ticker, timeframe, start, end, columns, market='shares', engine='stock'):
        with requests.Session() as session:
            try:
                data = apimoex.get_market_candles(session, ticker, timeframe, start, end,
                                                  columns, market, engine)
                if not data:
                    raise RequestException("moex")
            except Exception as e:
                raise RequestException("moex")
        return data

    @staticmethod
    def get_ticker_last_date(ticker, market='shares', engine='stock'):
        if market == 'index':
            ticker = ticker[1:]
        with requests.Session() as session:
            try:
                ticker_borders = apimoex.get_market_candle_borders(session, ticker, market, engine)
                if not ticker_borders:
                    raise RequestException("moex")
            except Exception as e:
                raise RequestException("moex")
        ticker_day_borders = ticker_borders[1]
        date_last = ticker_day_borders['end'][:10]
        return date_last

    @classmethod
    def query(cls, request_url: str, arguments=None):
        if arguments is None:
            arguments = {}
        with requests.Session() as session:
            try:
                iss = apimoex.ISSClient(session, cls.ISS_URL + request_url, arguments)
                response = iss.get()
            except Exception:
                raise RequestException("moex")
        return response
