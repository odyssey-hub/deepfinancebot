from numpy import mean, sign
from darts.metrics import rho_risk, quantile_loss

from chatbot.helpers.ParamHelpers.ParamHelper import ParamHelper


class Forecaster:

    PROB_NUM_SAMPLES = 500
    CV_NUM_WINDOWS = 2
    QUANTILES_EVAL = [0.25, 0.75]
    QUANTILES_OUT = [0.05, 0.1, 0.2, 0.25, 0.5, 0.75, 0.8, 0.9, 0.95]

    def __init__(self, ticker, timeframe, target, horizon, model_name,
                 is_prob, eval_horizon, period, curr_date):
        self.ticker = ticker
        self.timeframe = timeframe
        self.target = target
        self.model_name = model_name
        self.horizon = horizon
        self.is_prob = is_prob
        self.eval_horizon = eval_horizon
        self.curr_date = curr_date
        self.cv_step = eval_horizon
        self.period = period

        # if timeframe == 60:
        #     include_today = False
        # else:
        #     include_today = True
        include_today = True
        self.ts = ParamHelper.ts_from_param_period(ticker, timeframe, period, curr_date, include_today=include_today,
                                                   from_db=False)



    @staticmethod
    def mean_direction_acc(val, forecast):
        correct_direction = sign(forecast.values()[:3] - val.values()[:3])
        da = mean(correct_direction == 1)
        return da * 100

    @classmethod
    def mean_quantile_loss(cls, val, prob_forecast):
        losses = []
        for tau in cls.QUANTILES_EVAL:
            rr = quantile_loss(val, prob_forecast, tau=tau)
            losses.append(rr)
        return mean(losses)

    @classmethod
    def mean_rho_risk(cls, val, prob_forecast):
        risks = []
        for rho in cls.QUANTILES_EVAL:
            rr = rho_risk(val, prob_forecast, rho=rho)
            risks.append(rr)
        return mean(risks)