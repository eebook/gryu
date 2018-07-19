#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals


import logging
import telebot
import os
import copy
import hashlib

from flask import request, g, current_app
from telebot.util import extract_arguments

from . import tg_bot_bp
from ..common.utils import json
from ..common.database import db
from ..users.models import Users, ActivationKeys, EncryptedTokens
from ..users import infra
from ..users.domain import generate_api_token
from ..cache import RedisCache
from ..common.clients import EEBookClient, UrlMetadataClient
from ..common.exceptions import ServiceException

redis_cache = RedisCache()


# apihelper.proxy = {'http':'http://192.168.199.121:1087'}
# apihelper.proxy = {'https':'http://192.168.199.121:1087'}
# apihelper.proxy = {'https':'socks5://192.168.199.121:1086'}

LOGGER = logging.getLogger(__name__)
bot = telebot.TeleBot(os.getenv("TG_BOT_TOKEN", None))
# bot.set_webhook(url=os.getenv("TG_WEBHOOK_URL", "https://gryuint.nujeh.com/tg_bot/webhook"))

@tg_bot_bp.route('/webhook', methods=['POST'])
@json
def bot_webhook():
    if request.method == "POST":
        LOGGER.info("post")
        data = request.json
        LOGGER.info("data: {}".format(data))
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)

        LOGGER.info("update???{}".format(update))
        # user = Users.query.filter_by(username="knarfeh-tg").first()
        user = get_user(update.message)
        LOGGER.info(user.email)
        bot.process_new_updates([update])
        return {}

def get_user(message):
    """
    if not exist, create user
    """
    user = Users.query.filter_by(username=message.from_user.username+"-tg").first()
    if not user:
        LOGGER.info("User {} not exist, creating".format(message.from_user.username))
        username = message.from_user.username + "-tg"
        email = "tg_user_{}@eebook.com".format(username)
        # TODO: write password with env !!!
        # user = Users(username=username, email=email, password="nopassword", is_active=True)
        user_dict = {
            "username": username,
            "email": email,
            "password": "nopassword",
            "is_active": False
        }
        user = infra.create_user(user_dict)
        ActivationKeys.query.filter_by(user_id=user.id).first().delete()
        token = generate_api_token(user_dict, need_user_active=False)['token']
        redis_cache.writer.set("eebook-gryu-" + username, token)
    return user


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    token = redis_cache.writer.get("eebook-gryu-" + message.from_user.username + "-tg")
    # result = EEBookClient(token).get_job_config_list(None)
    # bot.reply_to(message, "Hello there")


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
    if len(args)%2 == 0:
        args.append(" ")
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
        # bot.reply_to(message, response_str)
        return

    submit_env_dict = dict(zip(args[1::2], args[2::2]))
    print("submit_env_dict: {}".format(submit_env_dict))

    if url_metadata["schema"] is not None:
        required_env_list = url_metadata["schema"].get("required", [])
    else:
        required_env_list = list()
    print("required_env_list: {}".format(required_env_list))

    missed_env = [item for item in required_env_list if item not in submit_env_dict.keys()]
    if len(missed_env) > 0:
        # bot.reply_to(message, ", ".join(missed_env) + " is required")
        return
    config_name = hashlib.md5((submit_str+message.from_user.username+"-tg").encode('utf-8')).hexdigest()
    print("config_name???{}".format(config_name))
    envvars = [{"name": k, "value": v} for k, v in submit_env_dict.items()]
    envvars.append({"name": "URL", "value": args[0]})
    print("envvars???{}".format(envvars))


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
    submit_str = extract_arguments(message.text.strip())
    return


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



@bot.message_handler(commands=["supported"])
def supported_url(message):
    """
    Get supported url
    Need improvement
    /supported
    """
    LOGGER.info("Get supported url, message: {}".foramt(message))
    # bot.reply_to(message, "https://eebook.github.io/catalog/")

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
