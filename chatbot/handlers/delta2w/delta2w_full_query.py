import os


from chatbot.exceptions.Delta2WException import Delta2WException
from finance.SpreadModelFull import SpreadModelFull
from app import bot, project_dir

DIFF_DEFAULT = 10


def delta2w_full(params_dict, chat_id):
    intervals = params_dict['interval']
    corrs = params_dict['corr']
    diffs = params_dict['diff']

    num_and = params_dict['AND']
    num_or = params_dict['OR']
    mode = detect_mode(num_and, num_or)

    if not diffs:
        diffs = list()
        for i in range(0, len(intervals)):
            diffs.append(DIFF_DEFAULT)

    if len(intervals) != len(corrs) or len(intervals) != len(diffs):
        raise Delta2WException("and_or_no_params")

    intervals, corrs, diffs = numerize_strings(intervals, corrs, diffs)
    validate_params(intervals, corrs)

    tickers = load_tickers('model_tickers.txt')
    bot.send_message(chat_id, f"Подождите, обработка займет время....")
    recommended_pairs = find_pairs(mode, num_and, num_or, tickers, intervals, corrs, diffs, chat_id)
    return recommended_pairs


def find_pairs(mode, num_and, num_or, tickers, intervals, corrs, diffs, chat_id):
    result_pairs = set()
    if mode == 'and':
        for i in range(0, num_and+1):
            model = SpreadModelFull(tickers, intervals[i], corrs[i], diffs[i])
            pairs = model.run()
            bot.send_message(chat_id, f"{i+1} проход: найдено {len(pairs)} пар")
            if not pairs:
                return tuple()
            elif i == 0:
                result_pairs = set(map(tuple, pairs))
            else:
                result_pairs = result_pairs.intersection(set(map(tuple, pairs)))
        result_pairs = [list(element) for element in result_pairs]
    elif mode == 'or':
        for i in range(0, num_or+1):
            model = SpreadModelFull(tickers, intervals[i], corrs[i], diffs[i])
            pairs = model.run()
            bot.send_message(chat_id, f"{i + 1} проход: найдено {len(pairs)} пар")
            if pairs:
                if i == 0:
                    result_pairs = set(map(tuple, pairs))
                else:
                    result_pairs = result_pairs.union(set(map(tuple, pairs)))
        result_pairs = [list(element) for element in result_pairs]
    else:
        model = SpreadModelFull(tickers, intervals[0], corrs[0], diffs[0], return_stats=True)
        result_pairs = model.run()

    return result_pairs


def validate_params(intervals, corrs):
    for interval in intervals:
        if interval <= 0 or interval > 300:
            raise Delta2WException("interval")
    for corr in corrs:
        if corr <= 0 or corr >= 1:
            raise Delta2WException("corr")


def detect_mode(num_and, num_or):
    if num_and is not None and num_or is not None:
        raise Delta2WException("and_or_only")
    elif num_and:
        return 'and'
    elif num_or:
        return 'or'
    else:
        return 'single'


def numerize_strings(intervals, corrs, diffs):
    try:
        intervals = [int(el) for el in intervals]
        corrs = [float(el) for el in corrs]
        diffs = [float(el) for el in diffs]
        return intervals, corrs, diffs
    except ValueError:
        raise Delta2WException("params")


def load_tickers(filename):
    path = os.path.join(project_dir, 'chatbot', 'db', 'tickers', filename)
    with open(path, "r") as file:
        tickers = file.read().splitlines()
    return tickers


