#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import telebot
from telebot.util import extract_arguments
from api.users.models import Users, EncryptedTokens
from api.common.clients import UrlMetadataClient
from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from api.common.exceptions import ServiceException

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

LOGGER = logging.getLogger(__name__)


def get_user(message):
    """
    if not exist, create user
    """
    user = session.query(Users).filter(Users.username==message.from_user.username+"-tg").first()
    # user = Users.query.filter_by(username="test").first()
    if not user:
        print("user {} not exist, creating".format(message.from_user.username))
        chat_id = message.chat.id
        name = message.text
        print("chat_id: {}, name: {}".format(chat_id, name))
        username = message.from_user.username + "-tg"
        email = "tg_user_{}@eebook.com".format(username)
        # TODO: write password with env
        user = Users(username=username, email=email, password="nopassword", is_active=True)
        session.add(user)
        session.commit()
    return user

def get_url_info_result(info):
    if info["schema"] is not None:
        env_dict = info["schema"].get("properties", {})
    else:
        env_dict = dict()

    variable_str = "\n"
    for key in env_dict.keys():
        default = env_dict[key].get("default", "REQUIRED")
        variable_str = variable_str + key + " " + str(default) + "\n"
    result = """
🎉🎉🎉 Yes, you can submit this url

Name: {}
Description: {}
Repository: {}
Variables:
{}

    """.format(info["name"], info["info"], info["repo"], variable_str)
    return result

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    print("message: {}".format(message))
    user = get_user(message)
    if not user:
        print("user not exist")
    bot.reply_to(message, "Hello there")

@bot.message_handler(commands=["submit"])
def submit_url(message):
    """
    /submit http://baidu.com
    """
    # http://wiki.jikexueyuan.com/project/explore-python/Standard-Modules/hashlib.html
    submit_str = extract_arguments(message.text.strip())
    if submit_str == "":
        bot.reply_to(message, "Please input an url, like /submit http://baidu.com")
        return
    args = submit_str.split(" ")
    url_metadata_payload = { "url": args[0] }
    try:
        url_metadata = UrlMetadataClient.get_url_metadata(url_metadata_payload)
        print("url_metadata??? {}".format(url_metadata))
    except ServiceException as s:
        if s.code == "url_not_support":
            # TODO: recommend similar url
            response_str = "Url not supported"
        else:
            response_str = "Something wrong, please contact @knarfeh"
        bot.reply_to(message, response_str)
        return
    print(url_metadata)
    submit_env = args[1::2]
    print("submit_env: {}".format(submit_env))
    if url_metadata["schema"] is not None:
        required_env_list = url_metadata["schema"].get("required", [])
    else:
        required_env_list = list()
    print("required_env_list: {}".format(required_env_list))
    missed_env = [item for item in required_env_list if item not in submit_env]
    if len(missed_env) > 0:
        bot.reply_to(message, ", ".join(missed_env) + " is required")
        return
    job_config_payload = {
        "config_name": "TODO",
        "image_name": url_metadata["image"],
        "envvars": [{
            "name": "URL",
            "value": args[0],
        },{

        }]
    }

    bot.reply_to(message, "test submit")


@bot.message_handler(commands=["url_info"])
def get_url_info(message):
    """
    /url_info http://baidu.com
    """
    url = extract_arguments(message.text.strip())
    print("get url info, url: {}".format(url))
    if url == "":
        bot.reply_to(message, "Please input an url, like /url_info http://baidu.com")
        return
    data = { "url": args[0] }
    try:
        url_metadata = UrlMetadataClient.get_url_metadata(data)
        response_str = get_url_info_result(url_metadata)
    except ServiceException as s:
        if s.code == "url_not_support":
            # TODO: recommend similar url
            response_str = "Url not supported"
        else:
            response_str = "Something wrong, please contact @knarfeh"

    bot.reply_to(message, response_str)


@bot.message_handler(commands=["supported"])
def supported_url(message):
    """
    Get supported url
    Need improvement
    /supported
    """
    print("get supported url, message: {}".format(message))
    bot.reply_to(message, "https://eebook.github.io/catalog/")


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

@bot.message_handler(commands=["run"])
def run_job(message):
    """
    run job with job config or job id
    /run job_config or job_uuid
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
