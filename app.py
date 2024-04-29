import os

import telebot

from chatbot.db.SQLite.DB import DB

bot = telebot.TeleBot('TOKEN')
project_dir = os.path.dirname(__file__)
db = DB(os.path.join(project_dir, 'BotDB.db'))
