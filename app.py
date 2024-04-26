import os

import telebot

from chatbot.db.SQLite.DB import DB

bot = telebot.TeleBot('6346571492:AAFF2VAFvfok54GeZNCO98ET8uTxapKvZ6s')
project_dir = os.path.dirname(__file__)
db = DB(os.path.join(project_dir, 'BotDB.db'))