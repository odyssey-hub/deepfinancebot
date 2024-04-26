from finance.forecasting.Forecaster import Forecaster
from darts import TimeSeries
from darts.models import BlockRNNModel, NHiTSModel, TCNModel
from darts.dataprocessing.transformers import Scaler
from darts.metrics.metrics import mae, smape
from finance.forecasting.nn_configs.nn_hyperopts import *
from ta import add_all_ta_features
from pandas import DataFrame, concat
from sklearn.feature_selection import f_regression, GenericUnivariateSelect, mutual_info_regression
from numpy import mean
import datetime as dt


class NNForecaster(Forecaster):

    NUM_FEATURES = 3
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
        if timeframe == 24 or timeframe == 7:
            self.num_evals = 1
        else:
            self.num_evals = 1



    def load_model(self):
        out = self.horizon
        match self.model_name:
            case 'rnn':
                if self.timeframe == 60:
                    self.model = BlockRNNModel(output_chunk_length=out, **rnn_conf_hour_det)
                    self.model_prob = BlockRNNModel(output_chunk_length=out, **rnn_conf_hour_prob)
                elif self.timeframe == 24:
                    if self.horizon == 1:
                        self.model = BlockRNNModel(output_chunk_length=out, **rnn_conf_day_det1)
                    else:
                        self.model = BlockRNNModel(output_chunk_length=out, **rnn_conf_day_det)
                    self.model_prob = BlockRNNModel(output_chunk_length=out, **rnn_conf_day_prob)
                else:
                    self.model = BlockRNNModel(output_chunk_length=out, **rnn_conf_week_det)
                    self.model_prob = BlockRNNModel(output_chunk_length=out, **rnn_conf_day_prob)
            case 'nhits':
                if self.timeframe == 60:
                    if self.horizon == 1:
                        self.model = NHiTSModel(output_chunk_length=out, **nhits_conf_hour_det1)
                    else:
                        self.model = NHiTSModel(output_chunk_length=out, **nhits_conf_hour_det)
                    self.model_prob = NHiTSModel(output_chunk_length=out, **nhits_conf_hour_prob)
                else:
                    if self.horizon == 1:
                        self.model = NHiTSModel(output_chunk_length=out, **nhits_conf_day_det1)
                    else:
                        self.model = NHiTSModel(output_chunk_length=out, **nhits_conf_day_det)
                    self.model_prob = NHiTSModel(output_chunk_length=out, **nhits_conf_day_prob)
            case 'tcn':
                if self.timeframe == 60:
                    self.model = TCNModel(output_chunk_length=out, **tcn_conf_hour_det)
                    self.model_prob = TCNModel(output_chunk_length=out, **tcn_conf_hour_prob)
                elif self.timeframe == 7:
                    self.model = NHiTSModel(output_chunk_length=out, **nhits_conf_day_det)
                    self.model_prob = NHiTSModel(output_chunk_length=out, **nhits_conf_day_prob)
                else:
                    self.model = TCNModel(output_chunk_length=out, **tcn_conf_day_det)
                    self.model_prob = TCNModel(output_chunk_length=out, **tcn_conf_day_prob)
            case _:
                self.model = BlockRNNModel(output_chunk_length=out, **rnn_conf_day_det)
                self.model_prob = BlockRNNModel(output_chunk_length=out, **rnn_conf_day_prob)

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
        scaler_train = Scaler()
        train_sc = scaler_train.fit_transform(ts)
        past_covs_sc = Scaler().fit_transform(past_covs)

        if self.is_prob:
            self.model_prob.fit(train_sc, past_covariates=past_covs_sc, verbose=0)
            prob_preds = self.model_prob.predict(series=train_sc, n=self.horizon, past_covariates=past_covs_sc,
                                                 num_samples=self.PROB_NUM_SAMPLES)
            prob_preds = scaler_train.inverse_transform(prob_preds)
            result = prob_preds.quantiles_df(self.QUANTILES_OUT).reset_index(drop=True)
        else:
            self.model.fit(train_sc, past_covariates=past_covs_sc, verbose=0)
            preds = self.model.predict(series=train_sc, n=self.horizon, past_covariates=past_covs_sc)
            preds = scaler_train.inverse_transform(preds)
            result = DataFrame(data=preds.values(), columns=[self.target])

        return result

    def eval(self):
        data = self.prepare_data()

        metrics = dict()
        for metric in ['mae', 'smape', 'qrisk', 'mda']:
            metrics[metric] = list()

        for i in range(0, self.num_evals):
            ts = TimeSeries.from_dataframe(data, value_cols=[self.target], freq='B')
            train, val = ts[:-self.eval_horizon], ts[-self.eval_horizon:]
            past_covs = TimeSeries.from_dataframe(data.drop(columns=['begin', self.target]), freq='B')
            scaler_train = Scaler()
            train_sc = scaler_train.fit_transform(train)
            past_covs_sc = Scaler().fit_transform(past_covs)

            if self.is_prob:
                self.model_prob.fit(train_sc, past_covariates=past_covs_sc, verbose=0)
                prob_preds = self.model_prob.predict(series=train_sc, n=self.eval_horizon, past_covariates=past_covs_sc,
                                                     num_samples=self.PROB_NUM_SAMPLES)
                prob_preds = scaler_train.inverse_transform(prob_preds)
                metrics['mae'].append(mae(val, prob_preds.quantile(0.5)))
                metrics['smape'].append(smape(val, prob_preds.quantile(0.5)))
                metrics['qrisk'] = self.mean_rho_risk(val, prob_preds)
            else:
                self.model.fit(train_sc, past_covariates=past_covs_sc, verbose=0)
                preds = self.model.predict(series=train_sc, n=self.eval_horizon, past_covariates=past_covs_sc)
                preds = scaler_train.inverse_transform(preds)
                metrics['mae'].append(mae(val, preds))
                metrics['smape'].append(smape(val, preds))
                metrics['mda'].append(self.mean_direction_acc(val, preds))
            data = data[:-self.cv_step]

        for metric in ['mae', 'smape', 'qrisk', 'mda']:
            metrics[metric] = mean(metrics[metric])
        return metrics