#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
import os
from api.users.models import Users
from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

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
Base = declarative_base()
Session = sessionmaker()
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session.configure(bind=engine)
session = Session()

def get_user(message):
    """
    if not exist, create user
    """
    user = session.query(Users).filter(Users.username==message.from_user.username+"-tg").first()
    # user = Users.query.filter_by(username="test").first()
    if not user:
        print("user not exist, creating")
        chat_id = message.chat.id
        name = message.text
        print("chat_id: {}, name: {}".format(chat_id, name))
        username = message.from_user.username + "-tg"
        email = "tg_user@eebook.com"
        user = Users(username=username, email=email, password="nopassword", is_active=True)
        session.add(user)
        session.commit()
    return user

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    print("message: {}".format(message))
    user = get_user(message)
    if not user:
        print("user not exist")
    bot.reply_to(message,
                 ("Hi there, I am EchoBot.\n"
                  "I am here to echo your kind words back to you."))

@bot.message_handler(commands=["submit"])
def submit_url(message):
    print("submit url, message: {}".format(message))
    bot.reply_to(message, ("test submit"))

if __name__ == "__main__":
    from telebot import apihelper
    apihelper.proxy = {'http':'http://0.0.0.0:1087'}
    bot.polling()
