import os

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import datetime as dt

from app import project_dir


class Visualizer:

    @classmethod
    def line_chart(cls, list_ts, column: str, out_mode='file', format='html'):
        df = pd.DataFrame()
        df['date'] = list_ts[0].column('begin')
        for ts in list_ts:
            df[ts.ticker] = ts.column(column)
        tickers = [ts.ticker for ts in list_ts]
        fig = px.line(df, x='date', y=tickers, title=f"График {tickers} по столбцу {column}")
        if out_mode == 'file':
            return cls.save_chart_as(fig, tickers, format)
        else:
            fig.show()
            return None

    @classmethod
    def candle_chart(cls, ts, out_mode='file', format='html'):
        fig = go.Figure(data=[go.Candlestick(x=ts.data['begin'],
                                             open=ts.data['open'],
                                             high=ts.data['high'],
                                             low=ts.data['low'],
                                             close=ts.data['close'])])
        if out_mode == 'file':
            return cls.save_chart_as(fig, ts.ticker, format)
        else:
            fig.show()
            return None

    @staticmethod
    def save_chart_as(fig, tickers, format):
        #project_dir = os.path.dirname(os.path.dirname(__file__))
        filename = f"chart_{tickers}_{dt.datetime.now().strftime('%d.%m.%Y_%H.%M.%S')}.{format}"
        path = os.path.join(project_dir, 'data', 'export', 'charts', filename)
        if format == 'html':
            fig.write_html(path)
        else:
            fig.write_image(path)
        return path