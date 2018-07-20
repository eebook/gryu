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
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)

        LOGGER.debug("update???{}".format(update))
        user, token = get_user(update.message)
        bot.process_new_updates([update])
        redis_cache.writer.set("eebook-gryu-"+user.username, token)
        redis_cache.writer.expire("eebook-gryu-"+user.username, 3600)
        return {}

def get_user(message):
    """
    if not exist, create user
    """
    user = Users.query.filter_by(username=message.from_user.username+"-tg").first()
    if not user:
        LOGGER.info("User {} not exist, creating".format(message.from_user.username))
        username = message.from_user.username + "-tg"
        email = "tg_user_{}@eebook.com".format(message.from_user.username)
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
        redis_cache.writer.set("eebook-gryu-"+username, token)
        redis_cache.writer.expire("eebook-gryu-"+username, 3600)
    else:
        token = EncryptedTokens.get_or_create(defaults=None, user_id=user.id)[0].key
    return user, token


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
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
    if len(args)%2 == 0:
        args.append(" ")
    url_metadata_payload = { "url": args[0] }
    try:
        url_metadata = UrlMetadataClient.get_url_metadata(url_metadata_payload)
        LOGGER.debug("URL metadata of {}: {}".format(args[0], url_metadata))
    except ServiceException as s:
        if s.code == "url_not_support":
            # TODO: recommend similar url
            response_str = "Url not supported"
        else:
            response_str = "Something wrong, please contact @knarfeh"
        # bot.reply_to(message, response_str)
        return

    submit_env_dict = dict(zip(args[1::2], args[2::2]))
    LOGGER.info("submit_env_dict: {}".format(submit_env_dict))

    if url_metadata["schema"] is not None:
        required_env_list = url_metadata["schema"].get("required", [])
    else:
        required_env_list = list()
    LOGGER.info("required_env_list: {}".format(required_env_list))

    missed_env = [item for item in required_env_list if item not in submit_env_dict.keys()]
    if len(missed_env) > 0:
        # bot.reply_to(message, ", ".join(missed_env) + " is required")
        return
    config_name = hashlib.md5((submit_str+message.from_user.username+"-tg").encode('utf-8')).hexdigest()
    LOGGER.info("config_name: {}".format(config_name))
    envvars = [{"name": k, "value": v} for k, v in submit_env_dict.items()]
    envvars.append({"name": "URL", "value": args[0]})
    job_config_payload = {
        "config_name": config_name,
        "image_name": url_metadata["image"],
        "created_by": message.from_user.username+"-tg",
        "envvars": envvars
    }
    token = redis_cache.writer.get("eebook-gryu-" + message.from_user.username + "-tg")
    try:
        EEBookClient(token).create_job_config(job_config_payload)
    except ServiceException as e:
        if e.code == "job_config_name_conflict":
            response_str = "Already exist, please try\n /run {} \n，input /configs see exist job config".format(config_name)
        else:
            response_str = "Something wrong, please contact @knarfeh"
        # bot.reply_to(message, response_str)
        return
    start_job_payload = {
        "config_name": config_name
    }
    try:
        EEBookClient(token).start_job(start_job_payload)
    except ServiceException as e:
        if e.code == "unknown_issue":
            response_str = "Something wrong, please contact @knarfeh"
        # bot.reply_to(message, response_str)
        return
    # bot.reply_to(message, "Working on it!")

@bot.message_handler(commands=["url_info"])
def get_url_info(message):
    """
    /url_info http://baidu.com
    """
    url = extract_arguments(message.text.strip())
    LOGGER.info("Get url info, url: {}".format(url))
    if url == "":
        bot.reply_to(message, "Please input an url, like /url_info http://baidu.com")
        return
    data = { "url": url}
    try:
        url_metadata = UrlMetadataClient.get_url_metadata(data)
        response_str = get_url_info_result(url_metadata)
    except ServiceException as s:
        if s.code == "url_not_support":
            # TODO: recommend similar url
            response_str = "Url not supported"
        else:
            response_str = "Something wrong, please contact @knarfeh"
    # bot.reply_to(message, response_str)
    LOGGER.info("response_str: {}".format(response_str))


@bot.message_handler(commands=["list"])
def list_resource(message):
    """
    Get a list of job config, job, books
    /list
    /list config
    /list config config_name list job of config_name

    /list job list all jobs
    /list jobs list all jobs

    /list book
    /list books
    """
    submit_str = extract_arguments(message.text.strip())
    if submit_str == "":
        return
    args = submit_str.split(" ")
    token = redis_cache.writer.get("eebook-gryu-" + message.from_user.username + "-tg")

    if args[0] == "config":
        LOGGER.info("List configs")
        job_config_result = EEBookClient(token).get_job_config_list(10, 1)
        result = get_list_job_config_result(job_config_result)
        # bot.reply_to(message, result)
        return
    elif args[0] == "jobs" or args[0] == "job":
        LOGGER.info("list jobs")
        # bot.reply_to(message, "list jobs")
        return
    elif args[0] == "books" or args[0] == "book":
        LOGGER.info("list books")
        # bot.reply_to(message, "list books")
        return

    bot.reply_to(message, "test list")


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
    if submit_str == "":
        return
    args = submit_str.split(" ")
    if len(args) < 2:
        LOGGER.info("Please specify a name to delete")
    token = redis_cache.writer.get("eebook-gryu-" + message.from_user.username + "-tg")
    LOGGER.info("TODO")

    if args[0] == "config":
        LOGGER.info("Delete config")
        return
    elif args[0] == "job" or args[0] == "jobs":
        LOGGER.info("Delete job")
        return
    elif args[0] == "books" or args[0] == "book":
        LOGGER.info("Delete book")
        return
    return


@bot.message_handler(commands=["detail, get"])
def get_resource(message):
    """
    get details of a resource
    /detail config
    /detail job
    /detail book
    """
    submit_str = extract_arguments(message.text.strip())
    if submit_str == "":
        return
    args = submit_str.split(" ")
    if len(args) < 2:
        LOGGER.info("Please specify a name to get detail")
    token = redis_cache.writer.get("eebook-gryu-" + message.from_user.username + "-tg")
    LOGGER.info("TODO")

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
🎉🎉🎉
Yes, you can submit this url

Name: {}
Description: {}
Repository: {}
Variables:
{}

    """.format(info["name"], info["info"], info["repo"], variable_str)
    return result

def get_list_job_config_result(job_configs):
    if len(job_configs["results"]) != 0:
        result = """
🎉🎉🎉
Your job configs:

"""
    else:
        result = """
Sorry, you don't have any job config
"""
    for job_config in job_configs["results"]:
        line = str(job_config["config_name"]) + "\n"
        result = result + line
    result = result + "\n Try /detail {{config}} to get the detail"
    return result
