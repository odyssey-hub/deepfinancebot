from darts import TimeSeries

from numpy import mean
from pandas import DataFrame, concat

from finance.forecasting.Forecaster import Forecaster
from darts.models import StatsForecastAutoETS, StatsForecastAutoARIMA
from darts.metrics.metrics import mae, smape
import datetime as dt

class StatsForecaster(Forecaster):

    def __init__(self, ticker, timeframe, target, horizon, model_name,
                 is_prob, eval_horizon, period, curr_date=dt.date.today()):
        super().__init__(ticker, timeframe, target, horizon, model_name,
                         is_prob, eval_horizon, period, curr_date)
        self.model = None
        self.load_model()
        if timeframe == 24 or timeframe == 7:
            self.num_evals = 4
        else:
            self.num_evals = 2

    def load_model(self):
        match self.model_name:
            case 'arima':
                self.model = StatsForecastAutoARIMA()
            case 'ets':
                self.model = StatsForecastAutoETS()
            case _:
                self.model = StatsForecastAutoARIMA()

    def prepare_data(self):
        df = self.ts.data[['begin', self.target]]
        df['begin'] = df['begin'].str[:10]
        return df

    def fit_predict(self):
        data = self.prepare_data()
        ts = TimeSeries.from_dataframe(data, value_cols=[self.target], freq='B')
        train = ts
        self.model.fit(train)
        preds = self.model.predict(self.horizon)
        preds = preds.values()
        result = DataFrame(data=preds, columns=[self.target])
        if self.is_prob:
            prob_preds = self.model.predict(self.horizon, num_samples=self.PROB_NUM_SAMPLES)
            result = prob_preds.quantiles_df(self.QUANTILES_OUT).reset_index(drop=True)
        return result

    def eval(self):
        data = self.prepare_data()

        metrics = dict()
        for metric in ['mae', 'smape', 'qrisk']:
            metrics[metric] = list()

        for i in range(0, self.num_evals):
            ts = TimeSeries.from_dataframe(data, value_cols=[self.target], freq='B')
            train, val = ts[:-self.eval_horizon], ts[-self.eval_horizon:]
            self.model.fit(train)
            preds = self.model.predict(self.eval_horizon)
            metrics['mae'].append(mae(val, preds))
            metrics['smape'].append(smape(val, preds))
            if self.is_prob:
                prob_preds = self.model.predict(self.eval_horizon, num_samples=self.PROB_NUM_SAMPLES)
                metrics['qrisk'] = self.mean_rho_risk(val, prob_preds)
            data = data[:-self.cv_step]

        for metric in ['mae', 'smape', 'qrisk']:
            metrics[metric] = mean(metrics[metric])

        return metrics





