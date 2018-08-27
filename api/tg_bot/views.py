#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import os
import copy
import telebot
import hashlib
import requests

from flask import request, g, current_app
from telebot import types
from telebot.util import extract_arguments


from . import tg_bot_bp
from ..common.utils import json
from ..users.models import Users, ActivationKeys, EncryptedTokens
from ..users import infra
from ..users.domain import generate_api_token
from ..cache import RedisCache
from ..common.clients import EEBookClient, UrlMetadataClient
from ..common.exceptions import ServiceException
from .utils import (pagination_edit_list_by_category, get_result_by_action_res, get_url_info_result,
                    delete_config, detail_config, start_job,
                    delete_job, detail_job)

bot = telebot.TeleBot(os.getenv("TG_BOT_TOKEN", None))
# bot.set_webhook(url=os.getenv("TG_WEBHOOK_URL", "https://gryuint.nujeh.com/tg_bot/webhook"))
TG_PASSWORD = os.getenv("TG_PASSWORD", "nopassword")
USER_TOKEN_EXPIRED = os.getenv("USER_TOKEN_EXPIRED", "3600")
LOGGER = logging.getLogger(__name__)


@tg_bot_bp.route('/webhook', methods=['POST'])
@json
def bot_webhook():
    if request.method == "POST":
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        username = update.message.from_user.username
        user, token = get_user(username)
        RedisCache().writer.set("eebook-gryu-"+user.username, token)
        # DO NOT modify update obj before the following line.
        bot.process_new_updates([update])
        RedisCache().writer.expire("eebook-gryu-"+user.username, USER_TOKEN_EXPIRED)
        return {}


@tg_bot_bp.route('/send_book', methods=['POST'])
@json
def send_book():
    # TODO: handle failed
    data = request.json.copy()
    LOGGER.info("Send book, data: {}".format(data))
    r = requests.get(data["book_url"])
    with open("/tmp/{}".format(data["book_name"]), 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    doc = open('/tmp/{}'.format(data["book_name"]), 'rb')
    bot.send_document(data["chat_id"], doc)
    os.remove('/tmp{}'.format(data["book_name"]))
    return {}


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    LOGGER.info("TODO: more friendly message")
    bot.reply_to(message, "Hello there")


@bot.message_handler(commands=["submit"])
def submit_url(message):
    """
    /submit http://baidu.com
    """
    # http://wiki.jikexueyuan.com/project/explore-python/Standard-Modules/hashlib.html
    # TODO: only run once a day
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
        bot.reply_to(message, response_str)
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
        bot.reply_to(message, ", ".join(missed_env) + " is required")
        return
    config_name = hashlib.md5((submit_str+message.from_user.username+"-tg").encode('utf-8')).hexdigest()
    envvars = [{"name": k, "value": v} for k, v in submit_env_dict.items()]
    envvars.append({"name": "URL", "value": args[0]})
    envvars.append({"name": "_CHAT_ID", "value": str(message.chat.id)})
    envvars.append({"name": "ES_INDEX", "value": url_metadata["name"]})
    job_config_payload = {
        "config_name": config_name,
        "image_name": url_metadata["image"],
        "created_by": message.from_user.username+"-tg",
        "envvars": envvars
    }
    LOGGER.info("Creating job config, payload: {}".format(job_config_payload))
    token = RedisCache().writer.get("eebook-gryu-" + message.from_user.username + "-tg")
    try:
        EEBookClient(token).create_job_config(job_config_payload)
    except ServiceException as e:
        if e.code == "job_config_name_conflict":
            response_str = "Already exist, please try\n /run {} \n，input /configs see existing job config".format(config_name)
        else:
            response_str = "Something wrong, please contact @knarfeh"
        LOGGER.info("Create job config, response string: {}".format(response_str))
        bot.reply_to(message, response_str)
        return
    start_job_payload = {
        "config_name": config_name
    }
    response_str = start_job(token, start_job_payload)
    LOGGER.info("Start a job, response string: %s", response_str)
    bot.reply_to(message, response_str)
    return


@bot.message_handler(commands=["url_info"])
def get_url_info(message):
    """
    /url_info http://baidu.com
    """
    url = extract_arguments(message.text.strip())
    LOGGER.info("Get url info, url: %s", url)
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
    LOGGER.info("Response string: %s", response_str)
    bot.reply_to(message, response_str)


@bot.message_handler(commands=["example", "examples"])
def url_example_by_type(message):
    # TODO
    pass


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
    args = submit_str.split(" ")
    markup = types.InlineKeyboardMarkup()

    if args[0] == "config" or args[0] == "configs":
        LOGGER.info("List configs")
        result, page_total = get_result_by_action_res(message, "list", "config", 1)
        if int(page_total) != 0:
            markup.add(
                types.InlineKeyboardButton("1", callback_data="current_page:"),
                types.InlineKeyboardButton(">>", callback_data="next:list_config-1")
            )
        LOGGER.info("List config, result: {}".format(result))
    elif args[0] == "job" or args[0] == "jobs":
        LOGGER.info("List jobs")
        result, page_total = get_result_by_action_res(message, "list", "job", 1)
        if int(page_total) != 0:
            markup.add(
                types.InlineKeyboardButton("1", callback_data="current_page:"),
                types.InlineKeyboardButton(">>", callback_data="next:list_job-1")
            )
        LOGGER.info("List jobs, result: {}".format(result))
    elif args[0] == "book" or args[0] == "books":
        LOGGER.info("list books")
    elif args[0] == "":
        LOGGER.info("/list")
        result = "/list_config \n /list_job \n list_book \n"
    else:
        result = "Unsupported resource"
    bot.reply_to(message, result, reply_markup=markup)


@bot.message_handler(commands=["detail"])
def get_resource(message):
    """
    get details of a resource
    /detail config
    /detail job
    /detail book
    """
    submit_str = extract_arguments(message.text.strip())
    args = submit_str.split(" ")
    token = RedisCache().writer.get("eebook-gryu-" + message.from_user.username + "-tg")
    markup = types.InlineKeyboardMarkup()

    if args[0] == "config" or args[0] == "configs":
        if len(args) == 1:
            LOGGER.info("no config name, list /detail_config_name")
            config_detail_result = detail_config(token, args[1])
            config_jobs_result, page_total = get_result_by_action_res(message, "list", "config", 1, header="Job configs: {}:\n".format(args[1]))
            if int(page_total) != 0:
                markup.add(
                    types.InlineKeyboardButton("1", callback_data="current_page:"),
                    types.InlineKeyboardButton(">>", callback_data="next:list_config-1".format(args[1]))
                )
        else:
            config_detail_result = detail_config(token, args[1])
            config_jobs_result, page_total = get_result_by_action_res(message, "detail", "config", 1, res_name=args[1], header="Jobs of {}:\n".format(args[1]))
            if int(page_total) != 0:
                markup.add(
                    types.InlineKeyboardButton("1", callback_data="current_page:"),
                    types.InlineKeyboardButton(">>", callback_data="next:detail_config/{}-1".format(args[1]))
                )
            LOGGER.info("Need tests!!!!")
            LOGGER.info("List config {}, result: {}".format(args[1], config_jobs_result))
        result = config_detail_result + "\n" + config_jobs_result
        LOGGER.debug("Got detailed config result: {}, args: {}".format(result, args))
    elif args[0] == "job" or args[0] == "jobs":
        if len(args) == 1:
            LOGGER.info("no jobname, list /detail_job_name")
            job_detail_result = detail_job(token, args[1])
            jobs_result, page_total = get_result_by_action_res(message, "list", "job", 1, res_name=None, header="Jobs:\n")
            if int(page_total) != 0:
                markup.add(
                    types.InlineKeyboardButton("1", callback_data="current_page:"),
                    types.InlineKeyboardButton(">>", callback_data="next:list_job-1")
                )
        else:
            job_id = "-".join(args[1:])
            LOGGER.info("Get detail of job %s", job_id)
            job_detail_result = detail_job(token, job_id)
            jobs_result = "/delete_job_" + job_id.replace("-", "_")
        result = job_detail_result + "\n" + jobs_result
        LOGGER.info("Detail jobs, result:\n{}".format(result))
    elif args[0] == "book" or args[0] == "books":
        pass
    elif args[0] == "":
        result = "/detail_config \n /detail_job \n /detail_book"
    # bot.reply_to(message, result)


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
    token = RedisCache().writer.get("eebook-gryu-" + message.from_user.username + "-tg")

    if args[0] == "config":
        LOGGER.info("Delete config %s", args[1])
        response_str = delete_config(token, args[1])
        bot.reply_to(message, response_str)
        return
    elif args[0] == "job" or args[0] == "jobs":
        LOGGER.info("Delete job: %s", args[1])
        response_str = delete_job(token, args[1])
        bot.reply_to(message, response_str)
        return
    elif args[0] == "books" or args[0] == "book":
        LOGGER.info("Delete book")
        # TODO
        return
    return


@bot.message_handler(commands=["edit", "update"])
def update_resource(message):
    """
    edit job config, book
    /edit config
    /edit book
    """
    LOGGER.info("TODO")
    # LOGGER.info("chat id???{}".format(message["chat"]))
    return


@bot.message_handler(commands=["run"])
def run_job(message):
    """
    run job with job config or job id
    /run job_config or job_uuid
    """
    # TODO
    pass


@bot.message_handler(commands=["supported"])
def supported_url(message):
    """
    Get supported url
    Need improvement
    /supported
    """
    # TODO
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
    # TODO
    pass


@bot.message_handler(commands=["report"])
def report_issue(message):
    """
    report an issue
    /report url  report url git repo, git issue
    /report contact @knarfeh
    """
    # TODO
    pass


@bot.message_handler(commands=["search"])
def donate(message):
    """
    search books
    """
    # TODO
    pass


@bot.message_handler(commands=["settings"])
def settings(message):
    """
    settings, including language, search feature(本站搜索，全网搜索)
    """
    # TODO
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
    # TODO
    pass


@bot.callback_query_handler(func=lambda call: True)
def process_callback_button(call):
    operator, query = call.data.split(":")
    if operator in ["prev", "next"]:
        LOGGER.info("pagination_edit_list_by_category")
        pagination_edit_list_by_category(call, operator, query)
    elif operator == "current_page":
        bot.answer_callback_query(callback_query_id=call.id, text='')


@bot.message_handler(func=lambda message: True)
def other_message(message):
    LOGGER.info("Handle other message")
    new_message_json = message.json
    cmd_args = new_message_json["text"].split("_")
    print("WTF is cmd_args???{}".format(cmd_args))
    if cmd_args[0].startswith("/") and cmd_args[0] not in ["/list", "/detail", "/delete"]:
        result = "Unsupported command"
        # bot.reply_to(message, result)
        return
    elif cmd_args[0].startswith("/") and cmd_args[0] in ["/list", "/detail", "/delete"]:
        new_message_json["text"] = " ".join(cmd_args)
        new_message = types.Message.de_json(new_message_json)
        bot.process_new_messages([new_message])
    # else
	# bot.reply_to(message, "search command???")

# admin command

# Utils
def get_user(_username):
    """
    if not exist, create user
    """
    user = Users.query.filter_by(username=_username+"-tg").first()
    if not user:
        LOGGER.info("User {} not exist, creating".format(_username))
        username = _username + "-tg"
        email = "tg_user_{}@eebook.com".format(_username)
        user_dict = {
            "username": username,
            "email": email,
            "password": TG_PASSWORD,
            "is_active": False
        }
        user = infra.create_user(user_dict)
        ActivationKeys.query.filter_by(user_id=user.id).first().delete()
        token = generate_api_token(user_dict, need_user_active=False)['token']
        RedisCache().writer.set("eebook-gryu-"+username, token)
        RedisCache().writer.expire("eebook-gryu-"+username, USER_TOKEN_EXPIRED)
    token = EncryptedTokens.get_or_create(defaults=None, user_id=user.id)[0].key
    return user, token
