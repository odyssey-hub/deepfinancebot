import os

import schedule

from app import bot, db, project_dir
from chatbot.db.Tickers import Tickers
from chatbot.handlers.delta2w.delta2w_full_cmd import export_results_xlsx
from finance.SpreadModelFull import SpreadModelFull


db_update_time = '02:00'
model_run_time = '03:00'
export_clean_time = '04:00'

test_chat_id = 5125851210


def config_schedule():
    schedule.every().day.at(db_update_time).do(update_db)
    schedule.every().day.at(model_run_time).do(model_run)
    schedule.every().day.at(export_clean_time).do(clean_export_data) #every monday!


def update_db():
    db.update_all_tickers(24)


def model_run():
    bot.send_message(test_chat_id, f'Модель - происходит поиск пар.......')
    model = SpreadModelFull(Tickers.get_tickers(), 20, 0.85, 10)
    pairs = model.run()
    path = export_results_xlsx(pairs)
    doc = open(path, 'rb')
    bot.send_message(test_chat_id, f'Модель - найдено {len(pairs)} пар.')
    bot.send_document(test_chat_id, doc)


def clean_folder(data_dir):
    for file in os.scandir(data_dir):
        os.remove(file.path)


def clean_export_data():
    export_dir = os.path.join(project_dir, 'data', 'export')
    charts_dir = os.path.join(export_dir, 'charts')
    model_full_dir = os.path.join(export_dir, 'model', 'full')
    model_mini_dir = os.path.join(export_dir, 'model', 'mini')
    tickers_dir = os.path.join(export_dir, 'tickers')
    dirs = (export_dir, charts_dir, model_mini_dir, model_full_dir, tickers_dir)
    for data_dir in dirs:
        clean_folder(data_dir)


def test_schedule():
    bot.send_message(test_chat_id, "Hello!")