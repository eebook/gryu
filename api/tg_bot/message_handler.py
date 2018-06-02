#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
import os
from ..users.models import Users

bot = telebot.TeleBot(os.getenv("TG_BOT_TOKEN"), None)

DB_USER = os.getenv("DB_USER", 'postgres')
DB_PASS = os.getenv("DB_PASS", None)
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_ENGINE = os.getenv("DB_ENGINE", "postgresql")
SQLALCHEMY_DATABASE_URI = '{db_engine}://{user_name}:{password}@{hostname}/{database}'.\
                            format_map({
                                'db_engine': DB_ENGINE,
                                'user_name': DB_USER,
                                'password': DB_PASS,
                                'hostname': DB_HOST,
                                'database': DB_NAME
                            })

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    user = Users.query.filter_by(username="test").first()
    print(user)
    bot.reply_to(message,
                 ("Hi there, I am EchoBot.\n"
                  "I am here to echo your kind words back to you."))


if __name__ == "__main__":
    from telebot import apihelper
    apihelper.proxy = {'http':'http://0.0.0.0:1087'}
    bot.polling()
