import logging
import os
import threading
import time

import schedule as schedule

from app import bot, project_dir

from chatbot.handlers.basic_commands.tickers import ticker_info_cmd
from chatbot.handlers.basic_commands.corr import corr_cmd
from chatbot.handlers.basic_commands.export import export_cmd
from chatbot.handlers.basic_commands.export import tickers_cmd
from chatbot.handlers.basic_commands.indices import indice_compound_cmd
from chatbot.handlers.basic_commands.indices import ticker_indices_cmd
from chatbot.handlers.basic_commands.stats import stats_values_cmd

from chatbot.handlers.additional_commands.chart import chart_cmd

from chatbot.handlers.delta2w import delta2w_min_cmd
from chatbot.handlers.delta2w import delta2w_full_cmd

from chatbot.handlers.forecast import forecast_cmd



@bot.message_handler(commands=['start'])
def start(message):
    path = os.path.join(project_dir, 'help', 'QueriesList.txt')
    with open(path, 'r', encoding='UTF-8') as file:
        hello_message = file.read()
    bot.send_message(message.chat.id,  hello_message)


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    mess = "Нет такой команды"
    bot.send_message(message.chat.id, mess)


@bot.edited_message_handler()
def message_edited(message):
    bot.send_message(message.chat.id, message.text)
    bot.process_new_messages([message])


if __name__ == '__main__':
    logging.basicConfig(filename='errors.log', encoding='utf-8', level=logging.ERROR,
                        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    #config_schedule()
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    print("Бот начал работу")
    while True:
        schedule.run_pending()
        time.sleep(1)
    #bot.infinity_polling()
    #bot.polling(non_stop=True)


