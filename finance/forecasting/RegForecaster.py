from darts import TimeSeries
from darts.models import XGBModel
from pandas import DataFrame, concat
from finance.forecasting.Forecaster import Forecaster
from sklearn.feature_selection import f_regression, GenericUnivariateSelect, mutual_info_regression
from darts.metrics.metrics import mae, smape
from numpy import mean
from ta import add_all_ta_features
import datetime as dt

class RegForecaster(Forecaster):

    NUM_FEATURES = 5
    BAD_INDICATORS = ['volatility_bbhi', 'volatility_bbli', 'volatility_kchi', 'volatility_kcli', 'trend_psar_down',
                      'trend_psar_up', 'trend_psar_up_indicator', 'trend_psar_down_indicator', 'trend_stc',
                      'trend_visual_ichimoku_a']

    def __init__(self, ticker, timeframe, target, horizon, model_name,
                 is_prob, eval_horizon, period, curr_date=dt.date.today()):
        super().__init__(ticker, timeframe, target, horizon, model_name,
                         is_prob, eval_horizon, period, curr_date)
        self.model = None
        self.model_prob = None
        self.load_model()

    def load_model(self):
        match self.model_name:
            case 'xgboost':
                self.model = XGBModel(lags_past_covariates=self.horizon, output_chunk_length=self.horizon)
                self.model_prob = XGBModel(lags_past_covariates=self.horizon, output_chunk_length=self.horizon,
                                           likelihood='poisson')
            case _:
                self.model = XGBModel(lags_past_covariates=self.horizon, output_chunk_length=self.horizon)
                self.model_prob = XGBModel(lags_past_covariates=self.horizon, output_chunk_length=self.horizon,
                                           likelihood='poisson')

    def prepare_data(self):
        df = self.ts.data
        df['begin'] = df['begin'].str[:10]
        df = add_all_ta_features(df, open='open', high='high', low='low', close='close', volume='volume',
                                    fillna=True)
        df = df.drop(columns=self.BAD_INDICATORS)
        df = df[43:]
        df = df.reset_index(drop=True)
        return self.sk_features(df)

    def sk_features(self, df, method='f_test'):
        if method == 'f_test':
            method = f_regression
        else:
            method = mutual_info_regression
        selector = GenericUnivariateSelect(method, mode='k_best', param=self.NUM_FEATURES)
        X = df.drop(columns=['begin', self.target])
        y = df[self.target]
        selector.fit_transform(X, y)
        importance = selector.scores_
        feature_importance = DataFrame({'Feature': X.columns, 'Scores': importance})
        feature_importance = feature_importance.sort_values('Scores', ascending=False)
        best_features = feature_importance['Feature'][:self.NUM_FEATURES].to_list()
        return df[['begin', self.target] + best_features]

    def fit_predict(self):
        data = self.prepare_data()
        ts = TimeSeries.from_dataframe(data, value_cols=[self.target], freq='B')
        past_covs = TimeSeries.from_dataframe(data.drop(columns=['begin', self.target]), freq='B')
        train = ts

        if self.is_prob:
            self.model_prob.fit(train, past_covariates=past_covs)
            prob_preds = self.model_prob.predict(self.horizon, past_covariates=past_covs, num_samples=self.PROB_NUM_SAMPLES)
            result = prob_preds.quantiles_df(self.QUANTILES_OUT).reset_index(drop=True)
        else:
            self.model.fit(train, past_covariates=past_covs)
            preds = self.model.predict(self.horizon, past_covariates=past_covs)
            result = DataFrame(data=preds.values(), columns=[self.target])

        return result


    def eval(self):
        data = self.prepare_data()
        metrics = dict()
        for metric in ['mae', 'smape', 'qrisk']:
            metrics[metric] = list()

        for i in range(0, 1):
            ts = TimeSeries.from_dataframe(data, value_cols=[self.target], freq='B')
            train, val = ts[:-self.eval_horizon], ts[-self.eval_horizon:]
            past_covs = TimeSeries.from_dataframe(data.drop(columns=['begin', self.target]), freq='B')
            if self.is_prob:
                self.model_prob.fit(train, past_covariates=past_covs)
                prob_preds = self.model_prob.predict(self.eval_horizon, past_covariates=past_covs,
                                                     num_samples=self.PROB_NUM_SAMPLES)
                metrics['mae'].append(mae(val, prob_preds.quantile(0.5)))
                metrics['smape'].append(smape(val, prob_preds.quantile(0.5)))
                metrics['qrisk'] = self.mean_rho_risk(val, prob_preds)
            else:
                self.model.fit(train, past_covariates=past_covs)
                preds = self.model.predict(self.eval_horizon, past_covariates=past_covs)
                metrics['mae'].append(mae(val, preds))
                metrics['smape'].append(smape(val, preds))
            data = data[:-self.cv_step]

        for metric in ['mae', 'smape', 'qrisk']:
            metrics[metric] = mean(metrics[metric])
        return metrics
