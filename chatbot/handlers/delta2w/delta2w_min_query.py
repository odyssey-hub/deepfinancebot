from chatbot.exceptions.Delta2WException import Delta2WException
from chatbot.exceptions.ParamException import ParamException
from finance.SpreadModelMini import SpreadModelMini


def delta2w(params_dict):
    tickers = params_dict['tickers']
    is_export = params_dict['export']
    try:
        interval = int(params_dict['interval'])
        corr = float(params_dict['corr'])
        diff = float(params_dict['diff'])
    except ValueError:
        raise Delta2WException("params")

    validate_params(tickers, interval, corr)

    model = SpreadModelMini(tickers, interval, corr, diff)
    recommended_pairs = model.run(is_export)
    export_path = model.export_path
    return recommended_pairs, export_path


def validate_params(tickers, interval, corr):
    if tickers is None:
        raise ParamException("no_tickers")
    elif len(tickers) < 2:
        raise ParamException("no_tickers")
    elif interval <= 0 or interval > 300:
        raise Delta2WException("interval")
    elif corr <= 0 or corr >= 1:
        raise Delta2WException("corr")

