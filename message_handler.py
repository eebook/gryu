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
        # TODO: add token
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
    """
    /submit http://baidu.com
    """
    print("submit url, message: {}".format(message))
    bot.reply_to(message, "test submit")


@bot.message_handler(commands=["url_info"])
def get_url_info(message):
    """
    /url_info http://baidu.com
    """
    print("get url info, message: {}".format(message))
    bot.reply_to(message, "test submit")


@bot.message_handler(commands=["supported"])
def supported_url(message):
    """
    Get supported url
    /supported
    """
    print("get supported url, message: {}".format(message))
    bot.reply_to(message, "test submit")


@bot.message_handler(commands=["list"])
def list_resource(message):
    """
    Get a list of job config, job, books
    /list config
    /list job
    /list book
    """
    print("get supported url, message: {}".format(message))
    bot.reply_to(message, "test submit")

@bot.message_handler(commands=["edit update"])
def update_resource(message):
    """
    edit job config, book
    /edit config
    /edit book
    """
    print("get supported url, message: {}".format(message))


@bot.message_handler(commands=["delete"])
def delete_resource(message):
    """
    Delete a resource
    /delete config
    /delete job
    /delete book
    """
    pass


@bot.message_handler(commands=["detail, get"])
def get_resource(message):
    """
    get details of a resource
    /detail config
    /detail job
    /detail book
    """
    pass


@bot.message_handler(commands=["logs"])
def job_logs(message):
    """
    get logs of a job
    /logs                   get logs of latest job
    /logs job_uuid          get logs of a job
    /logs 20                get 20 log of latest job
    /logs job_uuid 20       get 20 logs of a specific job
    """
    pass


@bot.message_handler(commands=["report"])
def report_issue(message):
    """
    report an issue
    /report url  report url git repo, git issue
    /report contact @knarfeh
    """
    pass


@bot.message_handler(commands=["search"])
def donate(message):
    """
    search books
    """
    pass


@bot.message_handler(commands=["settings"])
def donate(message):
    """
    settings, including language, search feature(本站搜索，全网搜索)
    """
    pass



@bot.message_handler(commands=["kindle"])
def kindle(message):
    """
    kindle
    """
    pass


@bot.message_handler(commands=["donate"])
def donate(message):
    """
    """
    pass



if __name__ == "__main__":
    from telebot import apihelper
    apihelper.proxy = {'http':'http://0.0.0.0:1087'}
    bot.polling()
